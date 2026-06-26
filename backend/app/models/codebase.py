"""Codebase model."""
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Enum, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Codebase(Base):
    """Codebase model representing a scanned codebase."""

    __tablename__ = "codebases"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_path = Column(String(1024), nullable=False)
    scanned_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    file_count = Column(Integer, default=0, nullable=False)
    status = Column(
        Enum("pending", "scanning", "completed", "failed", name="codebase_status"),
        default="pending",
        nullable=False,
        index=True,
    )
    error_message = Column(Text, nullable=True)
    meta_data = Column("metadata", JSON, nullable=False, default=dict)

    # Relationships
    project = relationship("Project", back_populates="codebases")
    extracted_queries = relationship("ExtractedQuery", back_populates="codebase", cascade="all, delete-orphan")
    query_groups = relationship("QueryGroup", back_populates="codebase", cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRun", back_populates="codebase", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of Codebase."""
        return f"<Codebase(id={self.id}, project_id={self.project_id}, status='{self.status}')>"

    def to_dict(self) -> dict[str, Any]:
        """Convert Codebase to dictionary."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "scan_path": self.scan_path,
            "scanned_at": self.scanned_at.isoformat() if self.scanned_at else None,
            "file_count": self.file_count,
            "status": self.status,
            "error_message": self.error_message,
            "metadata": self.meta_data,
        }
