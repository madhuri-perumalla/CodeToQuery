"""Location mapper for extracting code location information."""
import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class LocationMapper:
    """Mapper for extracting code location information."""

    def __init__(self) -> None:
        """Initialize location mapper."""
        pass

    def extract_location(
        self,
        file_path: str,
        line_number: int,
        content: str,
    ) -> Dict[str, Any]:
        """
        Extract location information from code.

        Args:
            file_path: File path
            line_number: Line number of the query
            content: File content

        Returns:
            Dictionary with location information
        """
        location = {
            "file_path": file_path,
            "line_number": line_number,
            "column_number": 0,
            "function_name": None,
            "class_name": None,
            "context_snippet": self._get_context_snippet(content, line_number),
            "call_stack": [],
        }

        # Detect file type and extract accordingly
        file_ext = Path(file_path).suffix.lower()

        if file_ext in [".js", ".jsx", ".ts", ".tsx"]:
            self._extract_javascript_location(content, line_number, location)
        elif file_ext == ".prisma":
            self._extract_prisma_location(content, line_number, location)

        return location

    def _get_context_snippet(self, content: str, line_number: int, context_lines: int = 3) -> str:
        """
        Get context snippet around a line.

        Args:
            content: File content
            line_number: Line number
            context_lines: Number of context lines before and after

        Returns:
            Context snippet
        """
        lines = content.split("\n")
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        
        snippet_lines = lines[start:end]
        return "\n".join(snippet_lines)

    def _extract_javascript_location(self, content: str, line_number: int, location: Dict[str, Any]) -> None:
        """
        Extract JavaScript/TypeScript location information.

        Args:
            content: File content
            line_number: Line number
            location: Location dictionary to update
        """
        lines = content.split("\n")
        target_line = lines[line_number - 1] if line_number <= len(lines) else ""

        # Find function name by looking backwards
        location["function_name"] = self._find_javascript_function(lines, line_number)
        location["class_name"] = self._find_javascript_class(lines, line_number)
        location["module_name"] = self._extract_module_name(content)

    def _find_javascript_function(self, lines: List[str], line_number: int) -> Optional[str]:
        """
        Find the function name containing a line.

        Args:
            lines: File lines
            line_number: Line number

        Returns:
            Function name or None
        """
        # Look backwards for function definition
        for i in range(line_number - 1, max(0, line_number - 20), -1):
            line = lines[i].strip()
            
            # Function declaration: function name() {}
            match = re.match(r'function\s+(\w+)\s*\(', line)
            if match:
                return match.group(1)
            
            # Method: name() {}
            match = re.match(r'(\w+)\s*\([^)]*\)\s*[{:]', line)
            if match:
                return match.group(1)
            
            # Arrow function: const name = () => {}
            match = re.match(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>', line)
            if match:
                return match.group(1)
            
            # Class method: name() {}
            match = re.match(r'(\w+)\s*\([^)]*\)\s*{', line)
            if match:
                return match.group(1)

        return None

    def _find_javascript_class(self, lines: List[str], line_number: int) -> Optional[str]:
        """
        Find the class name containing a line.

        Args:
            lines: File lines
            line_number: Line number

        Returns:
            Class name or None
        """
        # Look backwards for class definition
        for i in range(line_number - 1, max(0, line_number - 50), -1):
            line = lines[i].strip()
            
            # Class declaration: class Name {}
            match = re.match(r'class\s+(\w+)', line)
            if match:
                return match.group(1)

        return None

    def _extract_module_name(self, content: str) -> Optional[str]:
        """
        Extract module name from content.

        Args:
            content: File content

        Returns:
            Module name or None
        """
        # Look for module.exports or export default
        match = re.search(r'module\.exports\s*=\s*(\w+)', content)
        if match:
            return match.group(1)
        
        match = re.search(r'export\s+(?:default\s+)?(?:class|const|function)\s+(\w+)', content)
        if match:
            return match.group(1)
        
        return None

    def _extract_prisma_location(self, content: str, line_number: int, location: Dict[str, Any]) -> None:
        """
        Extract Prisma schema location information.

        Args:
            content: File content
            line_number: Line number
            location: Location dictionary to update
        """
        lines = content.split("\n")
        
        # Find model name
        location["function_name"] = self._find_prisma_model(lines, line_number)
        location["module_name"] = "prisma_schema"

    def _find_prisma_model(self, lines: List[str], line_number: int) -> Optional[str]:
        """
        Find the Prisma model name containing a line.

        Args:
            lines: File lines
            line_number: Line number

        Returns:
            Model name or None
        """
        # Look backwards for model definition
        for i in range(line_number - 1, max(0, line_number - 50), -1):
            line = lines[i].strip()
            
            # Model definition: model Name {}
            match = re.match(r'model\s+(\w+)', line)
            if match:
                return match.group(1)

        return None
