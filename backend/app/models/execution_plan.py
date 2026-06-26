"""Execution plan model."""
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Enum, Integer, Numeric, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class ExecutionPlan(Base):
    """Execution plan model representing PostgreSQL EXPLAIN results."""

    __tablename__ = "execution_plans"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("extracted_queries.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    plan_json = Column(JSON, nullable=False)
    plan_hash = Column(String(64), nullable=True, index=True)
    total_cost = Column(Numeric(20, 2), nullable=True)
    total_rows = Column(Numeric(20, 2), nullable=True)
    plan_width = Column(Integer, nullable=True)
    format = Column(
        Enum("json", "text", "xml", name="plan_format"),
        default="json",
        nullable=False,
    )
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    execution_time_ms = Column(Numeric(10, 2), nullable=True)
    meta_data = Column("metadata", JSON, nullable=False, default=dict)

    # Relationships
    query = relationship("ExtractedQuery", back_populates="execution_plan")
    diagnostics = relationship("Diagnostic", back_populates="execution_plan", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of ExecutionPlan."""
        return f"<ExecutionPlan(id={self.id}, query_id={self.query_id}, cost={self.total_cost})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert ExecutionPlan to dictionary."""
        return {
            "id": self.id,
            "query_id": self.query_id,
            "plan_json": self.plan_json,
            "plan_hash": self.plan_hash,
            "total_cost": float(self.total_cost) if self.total_cost else None,
            "total_rows": float(self.total_rows) if self.total_rows else None,
            "plan_width": self.plan_width,
            "format": self.format,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            "execution_time_ms": float(self.execution_time_ms) if self.execution_time_ms else None,
            "metadata": self.meta_data,
        }
