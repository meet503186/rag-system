from ..services import query_service


def query_rag(user_query, file_id):
    return query_service.process_query(user_query, file_id)