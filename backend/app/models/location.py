"""Query location model."""
from typing import Any

from sqlalchemy import JSON, Column, Integer, String, Text, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class QueryLocation(Base):
    """Query location model representing code location of a query."""

    __tablename__ = "query_locations"
    __table_args__ = (
        CheckConstraint("line_number > 0", name="valid_line_number"),
        CheckConstraint("column_number >= 0", name="valid_column_number"),
    )

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("extracted_queries.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String(1024), nullable=False, index=True)
    line_number = Column(Integer, nullable=False, index=True)
    column_number = Column(Integer, default=0, nullable=False)
    function_name = Column(String(255), nullable=True)
    class_name = Column(String(255), nullable=True)
    context_snippet = Column(Text, nullable=True)
    call_stack = Column(JSON, nullable=False, default=list)

    # Relationships
    query = relationship("ExtractedQuery", back_populates="locations")

    def __repr__(self) -> str:
        """String representation of QueryLocation."""
        return f"<QueryLocation(id={self.id}, query_id={self.query_id}, file='{self.file_path}')>"

    def to_dict(self) -> dict[str, Any]:
        """Convert QueryLocation to dictionary."""
        return {
            "id": self.id,
            "query_id": self.query_id,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "function_name": self.function_name,
            "class_name": self.class_name,
            "context_snippet": self.context_snippet,
            "call_stack": self.call_stack,
        }
