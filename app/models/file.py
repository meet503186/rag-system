from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from ..db.base import Base

class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    filename = Column(String)
    filepath = Column(String)

    size = Column(Integer)
    mime_type = Column(String)

    file_hash = Column(String, unique=True)

    page_count = Column(Integer)
    chunk_count = Column(Integer)

    status = Column(String, default="uploaded")

    uploaded_at = Column(DateTime, default=datetime.utcnow)
    indexed_at = Column(DateTime)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    user = relationship("User")