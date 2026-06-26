"""Fix suggestion model."""
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum,
    Integer,
    Numeric,
    String,
    Text,
    CheckConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class FixSuggestion(Base):
    """Fix suggestion model representing generated fix recommendations."""

    __tablename__ = "fix_suggestions"
    __table_args__ = (
        CheckConstraint("confidence_score >= 0 AND confidence_score <= 1", name="valid_confidence_score"),
    )

    id = Column(Integer, primary_key=True, index=True)
    diagnostic_id = Column(Integer, ForeignKey("diagnostics.id", ondelete="CASCADE"), nullable=False, index=True)
    suggestion_type = Column(
        Enum("add_index", "rewrite_query", "add_filter", "change_join_order", name="suggestion_type"),
        nullable=False,
        index=True,
    )
    description = Column(Text, nullable=False)
    sql_change = Column(Text, nullable=True)
    impact_estimate = Column(
        Enum("high", "medium", "low", name="impact_estimate"),
        nullable=True,
        index=True,
    )
    confidence_score = Column(Numeric(3, 2), nullable=True)
    meta_data = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    diagnostic = relationship("Diagnostic", back_populates="fix_suggestions")

    def __repr__(self) -> str:
        """String representation of FixSuggestion."""
        return f"<FixSuggestion(id={self.id}, type='{self.suggestion_type}', impact='{self.impact_estimate}')>"

    def to_dict(self) -> dict[str, Any]:
        """Convert FixSuggestion to dictionary."""
        return {
            "id": self.id,
            "diagnostic_id": self.diagnostic_id,
            "suggestion_type": self.suggestion_type,
            "description": self.description,
            "sql_change": self.sql_change,
            "impact_estimate": self.impact_estimate,
            "confidence_score": float(self.confidence_score) if self.confidence_score else None,
            "metadata": self.meta_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
