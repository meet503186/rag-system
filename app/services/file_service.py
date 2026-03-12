from fastapi import File
from sqlalchemy.orm import Session
import mimetypes

from fastapi import HTTPException
from sqlalchemy.orm import Session
import shutil
from pathlib import Path

from app.repositories import file_repository
from ingest import run_ingestion
from ..helpers.file import calculate_file_hash
from ..models.file import File as FileModel

UPLOAD_DIR = Path("docs").resolve()
UPLOAD_DIR.mkdir(exist_ok=True)

def process_upload(file: File, db: Session):
    try:

        file_path = UPLOAD_DIR / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # File metadata
        file_size = file_path.stat().st_size
        mime_type = mimetypes.guess_type(file.filename)[0]

        # Generate hash
        print("Generating hash")
        file_hash = calculate_file_hash(file_path)

        # Check duplicate
        print("Checking Duplicate")
        existing_file = db.query(FileModel).filter(
            FileModel.file_hash == file_hash
        ).first()

        if existing_file:
            raise HTTPException(
                status_code=400,
                detail="File already uploaded"
            )

        # Create DB record
        print("creating file in db")
        db_file = file_repository.create_file(db, {
            "filename": file.filename,
            "filepath": str(file_path),
            "size": file_size,
            "mime_type": mime_type,
            "file_hash": file_hash
        })

        # Run ingestion
        print("running ingestion")
        vector_db = run_ingestion(
            pdf_path=str(file_path),
            file_id=str(db_file.id)
        )

        # vector_db._collection.get({
        #     where={"file_id"}
        # })

        chunks = vector_db._collection.get(
            where={"file_id": str(db_file.id)}
        )

        chunk_count = len(chunks['ids'])


        # Update ingestion status
        file_repository.update_file(db, str(db_file.id), {"status": "indexed", "chunk_count": chunk_count})

        return {
            "file_id": db_file.id,
            "filename": db_file.filename,
            "size": db_file.size,
            "status": db_file.status
        }

    except Exception as e:
        print(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_all_files(db: Session):
    files = file_repository.get_all_files(db)
    return [
        {
            "file_id": str(f.id),
            "filename": f.filename,
            "size": f.size,
            "mime_type": f.mime_type,
            "page_count": f.page_count,
            "chunk_count": f.chunk_count,
            "status": f.status,
            "uploaded_at": f.uploaded_at,
            "indexed_at": f.indexed_at,
        }
        for f in files
    ]