from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.chunker.document_chunk import DocumentChunk


class DocumentChildChunk(Base):
    __tablename__ = "document_child_chunks"

    __table_args__ = (
        UniqueConstraint("parent_chunk_id", "chunk_index", name="uq_child_chunks_parent_index"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_chunk_id: Mapped[int] = mapped_column(ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)

    parent: Mapped["DocumentChunk"] = relationship(back_populates="children")