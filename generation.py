
import traceback

from llm import invoke_llm

def generate_answer(query, docs):
    try:
        context = "\n\n".join([doc.page_content for doc in docs])

        # prompt = f"""
        # Answer the question strictly based on the context below.

        # Question:
        # {query}

        # Context:
        # {context}

        # Instructions:
        #     - Only answer based on the given context.
        #     - If the answer is not explicitly present in the context,
        #     respond EXACTLY with:

        #     "The answer cannot be determined from the provided information."

        #     - If the answer in the context, simply returns the answer, no need of context detail or any extra explaination
        # """

        # prompt = f"""
        # You are a strict question-answering system.

        # Answer the question using ONLY the provided context.

        # Question:
        # {query}

        # Context:
        # {context}

        # Rules:
        # 1. Use only information from the context.
        # 2. If the answer is explicitly present in the context, return ONLY the answer.
        # 3. Do NOT include explanations or additional text.
        # 4. If the answer is NOT present in the context, respond EXACTLY with:

        # {FALLBACK_ANSWER}

        # 5. Do NOT rephrase the fallback sentence.
        # 6. Do NOT use outside knowledge.
        # """

        prompt = f"""
        Answer the question strictly based on the context below.

        Question:
        {query}

        Context:
        {context}

        Instructions:
            - Only answer based on the given context.
            - If the answer is not present in the context, you MUST respond with this EXACT phrase and nothing else:
            "The answer cannot be determined from the provided information."
            - Do NOT paraphrase, reword, or create variations of the above fallback phrase.
            - Do NOT say things like "X is not mentioned in the context" or "The context does not contain..."
            - If the answer IS in the context, return only the answer — no extra explanation or context details.
        """

        
        response = invoke_llm(prompt)

        return response
    except SystemExit:
        raise
    except Exception as e:
        print(f"[ERROR] Answer generation failed: {e}")
        traceback.print_exc()
        # sys.exit(1)
