"""Analysis run model."""
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Enum, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class AnalysisRun(Base):
    """Analysis run model representing an analysis execution."""

    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    codebase_id = Column(Integer, ForeignKey("codebases.id"), nullable=False, index=True)
    status = Column(
        Enum("pending", "running", "completed", "failed", "cancelled", name="analysis_status"),
        default="pending",
        nullable=False,
        index=True,
    )
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    meta_data = Column("metadata", JSON, nullable=False, default=dict)

    # Relationships
    codebase = relationship("Codebase", back_populates="analysis_runs")

    def __repr__(self) -> str:
        """String representation of AnalysisRun."""
        return f"<AnalysisRun(id={self.id}, codebase_id={self.codebase_id}, status='{self.status}')>"

    def to_dict(self) -> dict[str, Any]:
        """Convert AnalysisRun to dictionary."""
        return {
            "id": self.id,
            "codebase_id": self.codebase_id,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "metadata": self.meta_data,
        }
