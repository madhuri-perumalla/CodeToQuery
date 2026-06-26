"""Code scanner for recursive repository scanning."""
import os
from pathlib import Path
from typing import List, Set

from app.core.logging import get_logger

logger = get_logger(__name__)


class CodeScanner:
    """Scanner for recursively scanning code repositories."""

    # Default ignore patterns
    DEFAULT_IGNORE_PATTERNS = [
        "node_modules",
        ".git",
        ".idea",
        ".vscode",
        "dist",
        "build",
        "coverage",
        ".next",
        ".nuxt",
        "out",
        ".cache",
        "vendor",
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        ".venv",
        "venv",
        "env",
    ]

    # Supported file extensions
    SUPPORTED_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx", ".prisma", ".py", ".sql"}

    def __init__(self, ignore_patterns: List[str] | None = None) -> None:
        """
        Initialize code scanner.

        Args:
            ignore_patterns: Custom ignore patterns
        """
        self.ignore_patterns = set(ignore_patterns or self.DEFAULT_IGNORE_PATTERNS)
        self.scanned_files: Set[str] = set()

    def should_ignore(self, path: Path) -> bool:
        """
        Check if a path should be ignored.

        Args:
            path: Path to check

        Returns:
            True if path should be ignored
        """
        # Check if any part of the path matches ignore patterns
        for part in path.parts:
            for pattern in self.ignore_patterns:
                if pattern.startswith("*"):
                    # Wildcard pattern
                    if part.endswith(pattern[1:]):
                        return True
                elif part == pattern:
                    return True
        return False

    def scan_directory(self, root_path: str) -> List[Path]:
        """
        Recursively scan a directory for supported files.

        Args:
            root_path: Root directory path to scan

        Returns:
            List of file paths
        """
        root = Path(root_path)
        if not root.exists():
            raise FileNotFoundError(f"Directory not found: {root_path}")

        if not root.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {root_path}")

        logger.info(f"Starting scan of directory: {root_path}")
        files: List[Path] = []
        self.scanned_files = set()

        try:
            for item in root.rglob("*"):
                # Skip if should ignore
                if self.should_ignore(item):
                    continue

                # Only process files
                if not item.is_file():
                    continue

                # Check file extension
                if item.suffix not in self.SUPPORTED_EXTENSIONS:
                    continue

                files.append(item)
                self.scanned_files.add(str(item))

            logger.info(f"Scan complete. Found {len(files)} files")
            return files

        except PermissionError as e:
            logger.error(f"Permission error during scan: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during scan: {e}")
            raise

    def get_file_stats(self, root_path: str) -> dict:
        """
        Get statistics about scanned files.

        Args:
            root_path: Root directory path

        Returns:
            Dictionary with file statistics
        """
        files = self.scan_directory(root_path)
        
        stats = {
            "total_files": len(files),
            "by_extension": {},
            "by_directory": {},
        }

        for file in files:
            # Count by extension
            ext = file.suffix
            stats["by_extension"][ext] = stats["by_extension"].get(ext, 0) + 1

            # Count by directory
            parent = str(file.parent.relative_to(root_path))
            stats["by_directory"][parent] = stats["by_directory"].get(parent, 0) + 1

        return stats
