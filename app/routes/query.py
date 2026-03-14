import traceback

from app.dependencies.auth_guard import get_current_user
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.controllers import query_controller
from pipeline import run_query

router = APIRouter(prefix="/query")

class QueryRequest(BaseModel):
    question: str
    file_id: str

@router.post("/")
def query_rag(request: QueryRequest, current_user = Depends(get_current_user)):
    return query_controller.query_rag(request.question, request.file_id)

