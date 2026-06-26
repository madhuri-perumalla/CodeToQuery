"""SQL extraction service."""
import hashlib
from pathlib import Path
from typing import Any, Callable, Dict, List

from sqlalchemy.orm import Session

from app.core.errors import ExtractionError
from app.core.logging import get_logger
from app.models.codebase import Codebase
from app.models.query import ExtractedQuery
from app.models.location import QueryLocation
from app.services.extraction.code_scanner import CodeScanner
from app.services.extraction.location_mapper import LocationMapper
from app.services.extraction.parsers.prisma_parser import PrismaParser
from app.services.extraction.parsers.python_parser import PythonParser
from app.services.extraction.parsers.sequelize_parser import SequelizeParser
from app.services.extraction.parsers.sql_file_parser import SQLFileParser
from app.services.extraction.raw_sql_extractor import RawSQLExtractor
from app.services.normalization import ASTNormalizer

logger = get_logger(__name__)


class ExtractionService:
    """Service for extracting SQL queries from code."""

    def __init__(self) -> None:
        """Initialize extraction service."""
        self.scanner = CodeScanner()
        self.raw_sql_extractor = RawSQLExtractor()
        self.location_mapper = LocationMapper()
        self.sequelize_parser = SequelizeParser()
        self.prisma_parser = PrismaParser()
        self.python_parser = PythonParser()
        self.sql_file_parser = SQLFileParser()
        self.normalizer = ASTNormalizer()

    def extract_from_codebase(
        self,
        db: Session,
        codebase: Codebase,
        progress_callback: Callable | None = None,
    ) -> Dict[str, Any]:
        """
        Extract SQL queries from a codebase.

        Args:
            db: Database session
            codebase: Codebase model
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with extraction results

        Raises:
            ExtractionError: If extraction fails
        """
        logger.info(f"Starting extraction for codebase {codebase.id}")
        
        try:
            # Update codebase status
            codebase.status = "scanning"
            db.commit()

            # Scan directory for files
            files = self.scanner.scan_directory(codebase.scan_path)
            total_files = len(files)
            
            logger.info(f"Found {total_files} files to process")

            # Process each file
            all_queries: List[Dict[str, Any]] = []
            processed_files = 0
            total_queries = 0

            for file_path in files:
                try:
                    queries = self._extract_from_file(str(file_path))
                    all_queries.extend(queries)
                    total_queries += len(queries)
                    processed_files += 1

                    # Report progress
                    if progress_callback:
                        progress_callback(
                            processed_files=processed_files,
                            total_files=total_files,
                            current_file=str(file_path),
                            queries_found=total_queries,
                        )

                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")
                    continue

            # Store queries in database
            stored_count = self._store_queries(db, codebase, all_queries)

            # Update codebase status
            codebase.status = "completed"
            codebase.file_count = total_files
            codebase.meta_data = {
                "total_files": total_files,
                "total_queries": total_queries,
                "stored_queries": stored_count,
            }
            db.commit()

            logger.info(f"Extraction complete. Stored {stored_count} queries")

            return {
                "total_files": total_files,
                "total_queries": total_queries,
                "stored_queries": stored_count,
            }

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            codebase.status = "failed"
            codebase.error_message = str(e)
            db.commit()
            raise ExtractionError(f"Extraction failed: {e}", codebase.scan_path) from e

    def _extract_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract SQL queries from a single file.

        Args:
            file_path: Path to the file

        Returns:
            List of query dictionaries
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Could not read file {file_path}: {e}")
                return []
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return []

        queries: List[Dict[str, Any]] = []
        file_ext = Path(file_path).suffix.lower()

        # Extract based on file type
        if file_ext in [".js", ".jsx", ".ts", ".tsx"]:
            # Extract raw SQL
            raw_queries = self.raw_sql_extractor.extract_queries(content)
            queries.extend(raw_queries)

            # Extract Sequelize queries
            sequelize_queries = self.sequelize_parser.parse(file_path, content)
            queries.extend(sequelize_queries)

            # Extract Prisma queries
            prisma_queries = self.prisma_parser.parse(file_path, content)
            queries.extend(prisma_queries)

        elif file_ext == ".prisma":
            # Prisma schema file - extract raw SQL if any
            raw_queries = self.raw_sql_extractor.extract_queries(content)
            queries.extend(raw_queries)

        elif file_ext == ".py":
            # Python file - extract SQL from Python code
            python_queries = self.python_parser.parse(file_path, content)
            queries.extend(python_queries)

        elif file_ext == ".sql":
            # SQL file - extract SQL statements
            sql_queries = self.sql_file_parser.parse(file_path, content)
            queries.extend(sql_queries)

        # Add file path to all queries
        for query in queries:
            query["file_path"] = file_path

        return queries

    def _store_queries(
        self,
        db: Session,
        codebase: Codebase,
        queries: List[Dict[str, Any]],
    ) -> int:
        """
        Store extracted queries in the database.

        Args:
            db: Database session
            codebase: Codebase model
            queries: List of query dictionaries

        Returns:
            Number of queries stored
        """
        stored_count = 0

        for query_data in queries:
            try:
                # Generate query hash
                query_hash = self._generate_query_hash(query_data["normalized_sql"])

                # Check if query already exists
                existing = (
                    db.query(ExtractedQuery)
                    .filter(
                        ExtractedQuery.codebase_id == codebase.id,
                        ExtractedQuery.query_hash == query_hash,
                    )
                    .first()
                )

                if existing:
                    # Add location to existing query
                    self._add_location(db, existing, query_data)
                    continue

                # Create new query
                # Normalize SQL using AST normalizer
                normalized_sql = self.normalizer.canonical_form(query_data["normalized_sql"])
                
                query = ExtractedQuery(
                    codebase_id=codebase.id,
                    raw_sql=query_data["raw_sql"],
                    normalized_sql=normalized_sql,
                    query_hash=self._generate_query_hash(normalized_sql),
                    dialect="postgresql",
                    query_type=self._detect_query_type(normalized_sql),
                    source_type=query_data.get("source_type", "raw_sql"),
                    metadata=query_data.get("metadata", {}),
                )
                db.add(query)
                db.flush()

                # Add location
                self._add_location(db, query, query_data)

                stored_count += 1

            except Exception as e:
                logger.error(f"Error storing query: {e}")
                continue

        db.commit()
        return stored_count

    def _add_location(
        self,
        db: Session,
        query: ExtractedQuery,
        query_data: Dict[str, Any],
    ) -> None:
        """
        Add location information to a query.

        Args:
            db: Database session
            query: Query model
            query_data: Query data dictionary
        """
        try:
            # Read file content for location extraction
            with open(query_data["file_path"], "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            content = ""

        location_info = self.location_mapper.extract_location(
            query_data["file_path"],
            query_data.get("line_number", 1),
            content,
        )

        location = QueryLocation(
            query_id=query.id,
            file_path=location_info["file_path"],
            line_number=location_info["line_number"],
            column_number=location_info["column_number"],
            function_name=location_info["function_name"],
            class_name=location_info["class_name"],
            context_snippet=location_info["context_snippet"],
            call_stack=location_info["call_stack"],
        )
        db.add(location)

    def _generate_query_hash(self, sql: str) -> str:
        """
        Generate a hash for a SQL query.

        Args:
            sql: SQL query

        Returns:
            Query hash
        """
        # Use canonical form for hashing to ensure structural duplicates have same hash
        canonical_sql = self.normalizer.canonical_form(sql)
        return hashlib.sha256(canonical_sql.encode()).hexdigest()

    def _detect_query_type(self, sql: str) -> str | None:
        """
        Detect the type of SQL query.

        Args:
            sql: SQL query

        Returns:
            Query type (select, insert, update, delete, other)
        """
        sql_upper = sql.strip().upper()

        if sql_upper.startswith("SELECT"):
            return "select"
        elif sql_upper.startswith("INSERT"):
            return "insert"
        elif sql_upper.startswith("UPDATE"):
            return "update"
        elif sql_upper.startswith("DELETE"):
            return "delete"
        else:
            return "other"
