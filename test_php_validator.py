"""Unit tests for the PHP code validator."""

import sys
sys.path.insert(0, '/var/lib/alan-portfolio/workspaces/ryan/cobalt-console-144')

from php_validator import check_php_syntax, check_yield_from_with_comments
import pytest


class TestPHPValidator:
    """Test cases for PHP code validation."""

    def test_valid_php_syntax(self):
        """Valid PHP code should pass validation."""
        code = "<?php\n$x = 1;\nreturn $x;\n"
        result = check_php_syntax(code)
        assert result["valid"] is True, f"Expected valid, got: {result}"

    def test_invalid_yield_from_with_comment(self):
        """yield /* comment */ from should be detected as error (issue #14926)."""
        code = "function gen() { yield /* comment */ from gen2(); }"
        result = check_php_syntax(code)
        assert result["valid"] is False, \
            f"Expected invalid for yield with comment, got valid: {result}"
        assert any("comment" in e.lower() for e in result["errors"]), \
            f"Expected comment-related error, got: {result}"

    def test_valid_yield_from_no_comment(self):
        """yield from without comment should be valid."""
        code = "function gen() { yield from gen2(); }"
        result = check_php_syntax(code)
        # The validator should not flag yield from without comments as an error
        assert result["valid"] is True, f"Expected valid for clean yield from, got: {result}"

    def test_yield_with_single_line_comment(self):
        """yield // comment from should also be detected."""
        code = "function gen() { yield // comment from gen2(); }"
        result = check_php_syntax(code)
        assert result["valid"] is False, \
            f"Expected invalid for yield with line comment, got valid: {result}"

    def test_basic_structural_check(self):
        """Validator should detect yield-from-comment patterns."""
        code = "function gen() { yield /* comment */ from gen2(); }"
        result = check_php_syntax(code)
        assert result["valid"] is False, f"Expected invalid, got: {result}"

    def test_simple_assignment(self):
        """Simple valid assignment."""
        code = "$x = 42;"
        result = check_php_syntax(code)
        assert result["valid"] is True, f"Expected valid, got: {result}"

    def test_multiple_yield_from_patterns(self):
        """Multiple yield from patterns - only comment-containing ones should error."""
        code = """
function g1() { yield from gen1(); }
function g2() { yield /* comment */ from gen2(); }
function g3() { yield from gen3(); }
"""
        result = check_php_syntax(code)
        # Should detect the one with comment
        comment_errors = [e for e in result["errors"] if "comment" in e.lower()]
        assert len(comment_errors) >= 1, \
            f"Expected at least 1 comment error, got: {result}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
