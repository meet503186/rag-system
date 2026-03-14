from app.models.user import User
from sqlalchemy.orm import Session
from ..models.file import File as FileModel

def create_file(db: Session, file_data: dict):
    db_file = FileModel(
            **file_data,
            status="uploaded"
        )

    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def update_file(db: Session, file_id: str, file_data: dict):
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    for key, value in file_data.items():
        setattr(db_file, key, value)

    print(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

def get_all_files(db: Session):
    return db.query(FileModel).join(User).order_by(FileModel.uploaded_at.desc()).all()

def get_my_files(db: Session, current_user: User):
    return db.query(FileModel).filter(FileModel.user_id == current_user.id).order_by(FileModel.uploaded_at.desc()).all()

def get_file_by_file_hash(db: Session, file_hash: str):
    return db.query(FileModel).filter(FileModel.file_hash == file_hash).first()