from sqlalchemy.orm import Session

from ..services import file_service


def upload_file(file, db: Session):
    return file_service.process_upload(file, db)

def get_all_files(db: Session):
    return file_service.get_all_files(db)