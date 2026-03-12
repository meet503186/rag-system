import traceback

from pipeline import run_query

def query_rag(user_query, file_id):
    try:
        answer = run_query(user_query=user_query, file_id=file_id)
        return {"answer": answer.get("answer")}

    except Exception as e:
        print(f"❌ Query rag failed: {e}")
        traceback.print_exc()
        return {"error": "Query failed"}