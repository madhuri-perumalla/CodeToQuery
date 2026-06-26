"""Query group model."""
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    CheckConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class QueryGroup(Base):
    """Query group model representing grouped similar queries."""

    __tablename__ = "query_groups"
    __table_args__ = (
        CheckConstraint("similarity_threshold >= 0 AND similarity_threshold <= 1", name="valid_similarity_threshold"),
    )

    id = Column(Integer, primary_key=True, index=True)
    codebase_id = Column(Integer, ForeignKey("codebases.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    pattern_type = Column(String(50), nullable=False, index=True)  # duplicate, expensive, anti_pattern, common
    pattern_signature = Column(String(255), nullable=False, index=True)
    query_count = Column(Integer, default=0, nullable=False, index=True)
    files_impacted = Column(Integer, default=0, nullable=False)
    max_cost = Column(Numeric(20, 2), nullable=True, index=True)
    avg_cost = Column(Numeric(20, 2), nullable=True)
    total_cost = Column(Numeric(20, 2), nullable=True)
    max_rows = Column(Integer, nullable=True)
    avg_rows = Column(Integer, nullable=True)
    total_rows = Column(Integer, nullable=True)
    risk_score = Column(Numeric(5, 2), nullable=True, index=True)
    severity = Column(String(20), nullable=True, index=True)  # critical, high, medium, low
    sample_query_id = Column(Integer, ForeignKey("extracted_queries.id", ondelete="SET NULL"), nullable=True)
    similarity_threshold = Column(Numeric(3, 2), default=0.85, nullable=False)
    meta_data = Column("metadata", JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    codebase = relationship("Codebase", back_populates="query_groups")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of QueryGroup."""
        return f"<QueryGroup(id={self.id}, name='{self.name}', count={self.query_count})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert QueryGroup to dictionary."""
        return {
            "id": self.id,
            "codebase_id": self.codebase_id,
            "name": self.name,
            "pattern_type": self.pattern_type,
            "pattern_signature": self.pattern_signature,
            "query_count": self.query_count,
            "files_impacted": self.files_impacted,
            "max_cost": float(self.max_cost) if self.max_cost else None,
            "avg_cost": float(self.avg_cost) if self.avg_cost else None,
            "total_cost": float(self.total_cost) if self.total_cost else None,
            "max_rows": self.max_rows,
            "avg_rows": self.avg_rows,
            "total_rows": self.total_rows,
            "risk_score": float(self.risk_score) if self.risk_score else None,
            "severity": self.severity,
            "sample_query_id": self.sample_query_id,
            "similarity_threshold": float(self.similarity_threshold) if self.similarity_threshold else None,
            "metadata": self.meta_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class GroupMember(Base):
    """Group member model representing queries in a group."""

    __tablename__ = "group_members"
    __table_args__ = (
        CheckConstraint("similarity_score >= 0 AND similarity_score <= 1", name="valid_similarity_score"),
    )

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("query_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    query_id = Column(Integer, ForeignKey("extracted_queries.id", ondelete="CASCADE"), nullable=False, index=True)
    similarity_score = Column(Numeric(3, 2), nullable=False, index=True)
    is_representative = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    group = relationship("QueryGroup", back_populates="members")
    query = relationship("ExtractedQuery", back_populates="group_members")

    def __repr__(self) -> str:
        """String representation of GroupMember."""
        return f"<GroupMember(id={self.id}, group_id={self.group_id}, query_id={self.query_id})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert GroupMember to dictionary."""
        return {
            "id": self.id,
            "group_id": self.group_id,
            "query_id": self.query_id,
            "similarity_score": float(self.similarity_score) if self.similarity_score else None,
            "is_representative": bool(self.is_representative),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
