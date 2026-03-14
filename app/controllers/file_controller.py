from app.models.user import User
from sqlalchemy.orm import Session

from ..services import file_service


def upload_file(file, db: Session, current_user: User):
    return file_service.process_upload(file, db, current_user)

def get_all_files(db: Session):
    return file_service.get_all_files(db)

def get_my_files(db: Session, current_user: User):
    return file_service.get_my_files(db, current_user)