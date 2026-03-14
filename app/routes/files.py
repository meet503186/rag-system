
from app.dependencies.auth_guard import get_current_user
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from ..controllers import file_controller
from ..db.database import get_db

router = APIRouter(prefix="/files")

# Get all files
@router.get("/")
def get_all_files(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return file_controller.get_all_files(db)

# Get my files
@router.get("/my")
def get_my_files(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return file_controller.get_my_files(db, current_user)

# Upload a file
@router.post("/upload")
async def upload_file(file: UploadFile = File, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
   return file_controller.upload_file(file, db, current_user)
