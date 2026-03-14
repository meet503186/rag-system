from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.base import Base
from .routes import files, query, auth
from .db.database import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup logic
    Base.metadata.create_all(bind=engine)
    print("Database tables checked/created")

    yield

    # shutdown logic (optional)
    print("Application shutdown")


app = FastAPI(title="RAG API", lifespan=lifespan)

def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(files.router)
app.include_router(query.router)
app.include_router(auth.router)