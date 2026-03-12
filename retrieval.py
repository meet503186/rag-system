import sys
import traceback
from collections import defaultdict
from typing import List

from langchain_cohere import CohereRerank
from pydantic import BaseModel

from config import QUERY_VARIATIONS, RRF_K, RERANK_TOP_K, SIMILARITY_THRESHOLD
from llm import invoke_llm, extract_json


# ==============================
# QUERY EXPANSION
# ==============================

class QueryVariations(BaseModel):
    queries: List[str]


def generate_multiple_queries(original_query):
    try:
        # prompt = f"""
        # Generate {QUERY_VARIATIONS} different variations of this query
        # that would help retrieve relevant documents.

        # Original query: {original_query}

        # Return ONLY valid JSON in this format:
        # {{
        #     "queries": ["query1", "query2", "query3"]
        # }}
        # """

        # prompt = f"""
        # You are a JSON generator.

        # Your task:
        # Generate {QUERY_VARIATIONS} different variations of the given query
        # that would help retrieve relevant documents in a semantic search system.

        # Original query:
        # {original_query}

        # IMPORTANT RULES:
        # - Return strictly valid JSON.
        # - Do NOT include explanations.
        # - Do NOT include markdown.
        # - Do NOT include code blocks.
        # - Do NOT include text before or after the JSON.
        # - The output must be parseable by json.loads().
        # - Make sure the JSON is complete and properly closed. Do not truncate the output.

        # Required format:
        # {{
        #     "queries": ["query1", "query2", "query3"]
        # }}
        # """

        prompt = f"""
        Generate {QUERY_VARIATIONS} different variations of this query.
        Return them separated by ||| only.
        Do not include explanations.
        Do not include numbering.

        Original query:
        {original_query}
        """


        response = invoke_llm(prompt)

        queries = [q.strip() for q in response.split("|||") if q.strip()]

        return queries

        # parsed_json = extract_json(response)['queries']

        # print(parsed_json)

        # return parsed_json
    except Exception as e:
        print(f"[ERROR] Query generation failed: {e}")
        traceback.print_exc()
        # sys.exit(1)


# ==============================
# RRF IMPLEMENTATION
# ==============================

def reciprocal_rank_fusion(result_lists, k=RRF_K):
    try:
        scores = defaultdict(float)
        doc_map = {}

        for docs in result_lists:
            for rank, doc in enumerate(docs, start=1):
                doc_id = doc.metadata.get("id") or hash(doc.page_content)
                scores[doc_id] += 1 / (k + rank)
                doc_map[doc_id] = doc

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [(doc_map[doc_id], score) for doc_id, score in ranked]
    except Exception as e:
        print(f"[ERROR] Reciprocal rank fusion failed: {e}")
        traceback.print_exc()
        # sys.exit(1)


# ==============================
# RERANKER
# ==============================

def rerank_docs(documents, query):
    try:
        reranker = CohereRerank(
            model="rerank-english-v3.0",
            top_n=RERANK_TOP_K
        )
        return reranker.compress_documents(documents, query)
    except Exception as e:
        print(f"[ERROR] Reranking failed: {e}")
        traceback.print_exc()
        # sys.exit(1)



class SimilarityThresholdRetriever:
    def __init__(self, vectorstore, k, threshold=SIMILARITY_THRESHOLD):
        self.vectorstore = vectorstore
        self.k = k
        self.threshold = threshold

    def get_relevant_documents(self, query):
        results = self.vectorstore.similarity_search_with_score(query, k=self.k)

        docs = []
        for doc, distance in results:
            print(f"""
                Threshold: {self.threshold}, Distance: {distance}
                Doc: {doc.page_content[:100]}
            """)
            if distance <= self.threshold:
                docs.append(doc)

        print(f"[INFO] Retrieved {len(docs)} documents with distance <= {self.threshold}")
        return docs