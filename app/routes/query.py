import traceback

from fastapi import APIRouter
from pydantic import BaseModel
from app.controllers import query_controller
from pipeline import run_query

router = APIRouter(prefix="/query")

class QueryRequest(BaseModel):
    question: str
    file_id: str

@router.post("/")
def query_rag(request: QueryRequest):
    return query_controller.query_rag(request.question, request.file_id)

