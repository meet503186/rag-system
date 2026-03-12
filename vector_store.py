import hashlib
import sys
import traceback

from langchain_chroma import Chroma

from config import VECTOR_DB_DIRECTORY, embedding_model


def create_vector_store(chunks, persist_directory=VECTOR_DB_DIRECTORY):
    try:
        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model
        )

        ids = []
        texts = []
        metadatas = []

        for chunk in chunks:
            chunk_id = generate_chunk_id(chunk.metadata.get("original_content"))
            ids.append(chunk_id)
            texts.append(chunk.page_content)
            metadatas.append(chunk.metadata)

        vector_store.add_texts(
            texts=texts,
            ids=ids,
            metadatas=metadatas
        )

        print(f"Number of chunks stored: {vector_store._collection.count()}")
        return vector_store
    except Exception as e:
        print(f"[ERROR] Vector store creation failed: {e}")
        traceback.print_exc()
        # sys.exit(1)


def load_vector_store(persist_directory=VECTOR_DB_DIRECTORY):
    try:
        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model
        )
        count = vector_store._collection.count()
        print(f"Loaded vector store with {count} chunks.")
        return vector_store
    except Exception as e:
        print(f"[ERROR] Failed to load vector store: {e}")
        traceback.print_exc()
        # sys.exit(1)


def generate_chunk_id(text):
    return hashlib.sha256(text.encode()).hexdigest()
