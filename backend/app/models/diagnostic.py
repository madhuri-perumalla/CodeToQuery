"""Diagnostic model."""
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Enum, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Diagnostic(Base):
    """Diagnostic model representing rule-based diagnostic results."""

    __tablename__ = "diagnostics"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("execution_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = Column(String(100), nullable=False, index=True)
    severity = Column(
        Enum("critical", "warning", "info", name="severity"),
        nullable=False,
        index=True,
    )
    message = Column(Text, nullable=False)
    location = Column(JSON, nullable=True)
    meta_data = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    execution_plan = relationship("ExecutionPlan", back_populates="diagnostics")
    fix_suggestions = relationship("FixSuggestion", back_populates="diagnostic", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of Diagnostic."""
        return f"<Diagnostic(id={self.id}, rule_id='{self.rule_id}', severity='{self.severity}')>"

    def to_dict(self) -> dict[str, Any]:
        """Convert Diagnostic to dictionary."""
        return {
            "id": self.id,
            "plan_id": self.plan_id,
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
            "location": self.location,
            "metadata": self.meta_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
