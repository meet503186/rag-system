import sys
import traceback

from config import DENSE_K, FALLBACK_ANSWER, FUSION_TOP_K, SIMILARITY_THRESHOLD, SPARSE_K
from generation import generate_answer
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from retrieval import generate_multiple_queries, reciprocal_rank_fusion, rerank_docs
from vector_store import load_vector_store


bm25_cache = {}

def run_query(user_query: str, vector_store=None, file_id=None) -> dict:
    """
    Run the full RAG query pipeline.

    Args:
        user_query: The user's question.
        vector_store: Optional pre-loaded Chroma vector store. If None, loads from disk.

    Returns:
        dict with keys:
            "answer"  - the generated answer string
    """
    # STEP 1: LOAD VECTOR STORE
    if vector_store is None:
        vector_store = load_vector_store()

    # STEP 2: INITIALIZE RETRIEVERS
    search_kwargs = {
        "k": DENSE_K,
        "filter": {"file_id": file_id} if file_id else None
    }
    vector_retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
    # vector_retriever = SimilarityThresholdRetriever(vectorstore=vector_store, k=DENSE_K, threshold=SIMILARITY_THRESHOLD)

    if file_id:
        all_docs_raw = vector_store.get(where={"file_id": str(file_id)},include=["documents", "metadatas"])
    else:
        all_docs_raw = vector_store.get(include=["documents", "metadatas"])

    if(len(all_docs_raw["documents"]) == 0):
        return {"answer": "No documents found for the given file ID."}

    bm25_docs = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(all_docs_raw["documents"], all_docs_raw["metadatas"])
    ]

    if(bm25_cache.get(file_id) is None):
        bm25_cache[file_id] = BM25Retriever.from_texts(all_docs_raw["documents"])
        bm25_cache[file_id].k = SPARSE_K

    bm25_retriever = bm25_cache[file_id]

    # STEP 3: GENERATE QUERY VARIATIONS
    query_variations = generate_multiple_queries(user_query)

    # STEP 4: HYBRID RETRIEVAL (DENSE + SPARSE + RRF per variation)
    all_results = []
    for query in query_variations:
        dense_docs = vector_retriever.invoke(query)
        # dense_docs = vector_retriever.get_relevant_documents(query=query)
        sparse_docs = bm25_retriever.invoke(query)
        fused = reciprocal_rank_fusion([dense_docs, sparse_docs])
        fused_docs = [doc for doc, _ in fused[:FUSION_TOP_K]]
        all_results.append(fused_docs)

    print(f"""
       {all_results[0]}
    """)

    # STEP 5: CROSS-QUERY RRF FUSION
    final_fused = reciprocal_rank_fusion(all_results)
    final_docs = [doc for doc, _ in final_fused[:FUSION_TOP_K]]

    # STEP 6: RERANK WITH COHERE
    reranked_docs = rerank_docs(final_docs, user_query)

    print(f"""
    query: {user_query}
    Relevant docs after reranking:
    {[(doc.page_content[:10], doc.metadata["relevance_score"]) for doc in reranked_docs]}
""")
    filtered_docs = [
        doc for doc in reranked_docs
        if doc.metadata["relevance_score"] < SIMILARITY_THRESHOLD
    ]

    if(len(filtered_docs) == 0):
        return {"answer": FALLBACK_ANSWER}

    # STEP 7: GENERATE FINAL ANSWER
    answer = generate_answer(user_query, filtered_docs)

    # sources = [doc.page_content for doc in reranked_docs]

    return {"answer": answer}


def main():
    while True:
        user_query = input("Enter your query: ")

        print("\n" + "="*80)
        try:
            result = run_query(user_query)
        except Exception as e:
            print(f"[ERROR] Pipeline failed: {e}")
            traceback.print_exc()
            # sys.exit(1)

        print("\n==============================")
        print("FINAL ANSWER:")
        print("==============================")
        print(result["answer"])
        # print("\nSources used:")
        # for i, src in enumerate(result["sources"], 1):
        #     print(f"  {i}. {src[:120]}...")
        # print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        traceback.print_exc()
