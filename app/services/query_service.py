from app.repositories.query_repository import query_rag


def process_query(user_query, file_id):
    return query_rag(user_query=user_query, file_id=file_id)