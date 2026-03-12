import sys
import traceback

from ingestion import partition_document, create_chunks_by_title, summarize_chunks
from vector_store import create_vector_store


def run_ingestion(pdf_path: str, file_id: str = None):
    # STEP 1: PARTITION PDF
    print("\n" + "="*80)
    print("STEP 1: PARTITION PDF")
    print("="*80)
    try:
        elements = partition_document(pdf_path)
    except SystemExit:
        raise
    except Exception as e:
        print(f"[ERROR] Step 1 - PDF partitioning failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # STEP 2: CHUNK BY TITLE
    print("\n" + "="*80)
    print("STEP 2: CHUNK BY TITLE")
    print("="*80)
    try:
        chunks = create_chunks_by_title(elements)
    except SystemExit:
        raise
    except Exception as e:
        print(f"[ERROR] Step 2 - Chunking failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # STEP 3: AI SUMMARIZATION
    print("\n" + "="*80)
    print("STEP 3: AI SUMMARIZATION")
    print("="*80)
    try:
        summarized_chunks = summarize_chunks(chunks=chunks, file_id=file_id)
    except SystemExit:
        raise
    except Exception as e:
        print(f"[ERROR] Step 3 - Summarization failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # STEP 4: STORE IN VECTOR DB
    print("\n" + "="*80)
    print("STEP 4: STORE IN VECTOR DB")
    print("="*80)
    try:
        vector_store = create_vector_store(chunks=summarized_chunks)
        print("✅ Ingestion complete. Embeddings stored in vector DB.\n")
        return vector_store
    except SystemExit:
        raise
    except Exception as e:
        print(f"[ERROR] Step 4 - Vector store creation failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "./docs/diet.pdf"
    try:
        run_ingestion(pdf_path)
    except Exception as e:
        print(f"❌ Ingestion pipeline failed: {e}")
        traceback.print_exc()
