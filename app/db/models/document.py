from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, Enum as SQLEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
class DocumentStatus(str, Enum):
    uploaded = "uploaded"
    processing = "processing"
    ready = "ready"
    failed = "failed"

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500),nullable=False,)
    content_type: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[DocumentStatus] = mapped_column(SQLEnum(DocumentStatus),default=DocumentStatus.uploaded,)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)