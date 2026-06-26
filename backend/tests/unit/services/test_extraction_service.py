"""Tests for SQL extraction service."""
import pytest

from app.services.extraction.code_scanner import CodeScanner
from app.services.extraction.raw_sql_extractor import RawSQLExtractor
from app.services.extraction.location_mapper import LocationMapper
from app.services.extraction.parsers.sequelize_parser import SequelizeParser
from app.services.extraction.parsers.prisma_parser import PrismaParser


class TestCodeScanner:
    """Tests for CodeScanner."""

    def test_init(self):
        """Test scanner initialization."""
        scanner = CodeScanner()
        assert scanner.SUPPORTED_EXTENSIONS == {".js", ".jsx", ".ts", ".tsx", ".prisma"}

    def test_should_ignore_node_modules(self):
        """Test that node_modules is ignored."""
        scanner = CodeScanner()
        from pathlib import Path
        path = Path("/project/node_modules/package/index.js")
        assert scanner.should_ignore(path) is True

    def test_should_ignore_build(self):
        """Test that build folders are ignored."""
        scanner = CodeScanner()
        from pathlib import Path
        path = Path("/project/dist/index.js")
        assert scanner.should_ignore(path) is True

    def test_should_not_ignore_source(self):
        """Test that source files are not ignored."""
        scanner = CodeScanner()
        from pathlib import Path
        path = Path("/project/src/index.js")
        assert scanner.should_ignore(path) is False


class TestRawSQLExtractor:
    """Tests for RawSQLExtractor."""

    def test_extract_sql_strings(self):
        """Test SQL string extraction."""
        extractor = RawSQLExtractor()
        content = 'const query = `SELECT * FROM users WHERE id = ?`;'
        queries = extractor.extract_sql_strings(content)
        assert len(queries) == 1
        assert queries[0][1] == "SELECT * FROM users WHERE id = ?"

    def test_extract_single_quoted(self):
        """Test single-quoted SQL strings."""
        extractor = RawSQLExtractor()
        content = "const query = 'SELECT * FROM users';"
        queries = extractor.extract_sql_strings(content)
        assert len(queries) == 1

    def test_extract_double_quoted(self):
        """Test double-quoted SQL strings."""
        extractor = RawSQLExtractor()
        content = 'const query = "SELECT * FROM users";'
        queries = extractor.extract_sql_strings(content)
        assert len(queries) == 1

    def test_clean_sql(self):
        """Test SQL cleaning."""
        extractor = RawSQLExtractor()
        sql = "SELECT * FROM users WHERE id = ${userId}"
        cleaned = extractor.clean_sql(sql)
        assert "${userId}" not in cleaned
        assert "?" in cleaned

    def test_extract_queries(self):
        """Test query extraction."""
        extractor = RawSQLExtractor()
        content = 'const query = `SELECT * FROM users WHERE id = ?`;'
        queries = extractor.extract_queries(content)
        assert len(queries) == 1
        assert queries[0]["source_type"] == "raw_sql"


class TestSequelizeParser:
    """Tests for SequelizeParser."""

    def test_parse_findAll(self):
        """Test findAll parsing."""
        parser = SequelizeParser()
        content = "User.findAll({ where: { id: 1 } })"
        queries = parser.parse("test.js", content)
        assert len(queries) == 1
        assert queries[0]["metadata"]["method"] == "findAll"
        assert queries[0]["metadata"]["model"] == "User"

    def test_parse_create(self):
        """Test create parsing."""
        parser = SequelizeParser()
        content = "User.create({ name: 'John' })"
        queries = parser.parse("test.js", content)
        assert len(queries) == 1
        assert queries[0]["metadata"]["method"] == "create"

    def test_parse_update(self):
        """Test update parsing."""
        parser = SequelizeParser()
        content = "User.update({ name: 'Jane' }, { where: { id: 1 } })"
        queries = parser.parse("test.js", content)
        assert len(queries) == 1
        assert queries[0]["metadata"]["method"] == "update"


class TestPrismaParser:
    """Tests for PrismaParser."""

    def test_parse_findMany(self):
        """Test findMany parsing."""
        parser = PrismaParser()
        content = "prisma.user.findMany({ where: { id: 1 } })"
        queries = parser.parse("test.ts", content)
        assert len(queries) == 1
        assert queries[0]["metadata"]["method"] == "findMany"
        assert queries[0]["metadata"]["model"] == "user"

    def test_parse_create(self):
        """Test create parsing."""
        parser = PrismaParser()
        content = "prisma.user.create({ data: { name: 'John' } })"
        queries = parser.parse("test.ts", content)
        assert len(queries) == 1
        assert queries[0]["metadata"]["method"] == "create"

    def test_parse_delete(self):
        """Test delete parsing."""
        parser = PrismaParser()
        content = "prisma.user.delete({ where: { id: 1 } })"
        queries = parser.parse("test.ts", content)
        assert len(queries) == 1
        assert queries[0]["metadata"]["method"] == "delete"


class TestLocationMapper:
    """Tests for LocationMapper."""

    def test_extract_location(self):
        """Test location extraction."""
        mapper = LocationMapper()
        content = """
function getUser(id) {
    const query = 'SELECT * FROM users WHERE id = ?';
    return query;
}
"""
        location = mapper.extract_location("test.js", 3, content)
        assert location["file_path"] == "test.js"
        assert location["line_number"] == 3
        assert location["function_name"] == "getUser"

    def test_get_context_snippet(self):
        """Test context snippet extraction."""
        mapper = LocationMapper()
        content = "line1\nline2\nline3\nline4\nline5"
        snippet = mapper._get_context_snippet(content, 3, context_lines=1)
        assert "line2" in snippet
        assert "line3" in snippet
        assert "line4" in snippet
