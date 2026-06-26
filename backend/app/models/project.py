"""Project model."""
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Project(Base):
    """Project model representing a code analysis project."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    config = Column(JSON, nullable=False, default=dict)

    # Relationships
    owner = relationship("User", back_populates="projects")
    codebases = relationship("Codebase", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of Project."""
        return f"<Project(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert Project to dictionary."""
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "config": self.config,
        }
