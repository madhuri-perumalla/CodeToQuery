"""Extracted query model."""
from datetime import datetime
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
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ExtractedQuery(Base):
    """Extracted query model representing a SQL query from code."""

    __tablename__ = "extracted_queries"

    id = Column(Integer, primary_key=True, index=True)
    codebase_id = Column(Integer, ForeignKey("codebases.id", ondelete="CASCADE"), nullable=False, index=True)
    raw_sql = Column(Text, nullable=False)
    normalized_sql = Column(Text, nullable=False)
    query_hash = Column(String(64), nullable=False, index=True)
    dialect = Column(String(50), default="postgresql", nullable=False)
    query_type = Column(
        Enum("select", "insert", "update", "delete", "other", name="query_type"),
        nullable=True,
        index=True,
    )
    source_type = Column(
        Enum(
            "raw_sql",
            "orm_sequelize",
            "orm_typeorm",
            "orm_sqlalchemy",
            "orm_django",
            "orm_prisma",
            name="source_type",
        ),
        nullable=True,
        index=True,
    )
    cost = Column(Numeric(20, 2), nullable=True, index=True)
    execution_time = Column(Numeric(10, 2), nullable=True)
    health_score = Column(Integer, nullable=True)
    status = Column(
        Enum("healthy", "warning", "critical", "analyzing", name="query_status"),
        nullable=True,
        default="analyzing",
        index=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    meta_data = Column("metadata", JSON, nullable=False, default=dict)

    # Relationships
    codebase = relationship("Codebase", back_populates="extracted_queries")
    locations = relationship("QueryLocation", back_populates="query", cascade="all, delete-orphan")
    execution_plan = relationship("ExecutionPlan", back_populates="query", uselist=False, cascade="all, delete-orphan")
    group_members = relationship("GroupMember", back_populates="query", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of ExtractedQuery."""
        return f"<ExtractedQuery(id={self.id}, codebase_id={self.codebase_id}, hash='{self.query_hash[:8]}...')>"

    def to_dict(self) -> dict[str, Any]:
        """Convert ExtractedQuery to dictionary."""
        return {
            "id": self.id,
            "codebase_id": self.codebase_id,
            "raw_sql": self.raw_sql,
            "normalized_sql": self.normalized_sql,
            "query_hash": self.query_hash,
            "dialect": self.dialect,
            "query_type": self.query_type,
            "source_type": self.source_type,
            "cost": float(self.cost) if self.cost else None,
            "execution_time": float(self.execution_time) if self.execution_time else None,
            "health_score": self.health_score,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.meta_data,
        }
