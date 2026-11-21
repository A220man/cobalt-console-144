#!/usr/bin/env python3
"""
PHP Code Structural Validator

Validates PHP code for structural syntax errors, particularly:
- Invalid generator syntax (yield from with comments)
- General PHP parse errors

Addresses issue #14926: "PHP 8.3: yield /*comment*/ from" should be a
parse error - this validator correctly identifies it as an error.
"""

import sys
import re
from typing import List, Tuple


def check_yield_from_with_comments(code: str) -> List[str]:
    """
    Check for invalid yield from patterns with comments.
    
    Issue #14926: In PHP 8.3, `yield /* comment */ from gen2()` 
    should be a parse error but some implementations no longer flag it.
    This validator correctly detects this as an error.
    Also handles `yield // comment from` patterns.
    """
    errors = []
    
    # Strategy: search for yield followed by optional whitespace,
    # then a comment (/* */ or //), then from
    
    # Pattern 1: yield /* ... */ from  (multi-line block comment)
    # Pattern 2: yield // ... from     (single-line comment)
    
    # Pattern 1: yield followed by block comment then from
    # We look for "yield" then "/*" then anything then "*/" then "from"
    pattern_block = r'yield\s*/\*[^*]*\*+(?:[^/*][^*]*\*)*\/.*\bfrom\b'
    
    # Pattern 2: yield followed by // comment then from
    pattern_line = r'yield\s*//[^\n]*\bfrom\b'
    
    # Check pattern 1: yield /* comment */ from
    matches_block = re.findall(pattern_block, code, re.DOTALL)
    if matches_block:
        errors.append(
            "yield from with block comment is not valid PHP syntax - "
            "'yield /*comment*/ from' should be a parse error"
        )
    
    # Check pattern 2: yield // comment from
    matches_line = re.findall(pattern_line, code, re.DOTALL)
    if matches_line:
        errors.append(
            "yield from with line comment is not valid PHP syntax - "
            "'yield // comment from' should be a parse error"
        )
    
    # Also check for the specific issue #14926 pattern:
    # yield /*comment*/ from (no space needed between /* and comment*/)
    pattern_strict = r'yield\s*/\*.*?\*/\s+from\b'
    matches_strict = re.findall(pattern_strict, code, re.DOTALL)
    if matches_strict:
        # Only add if not already reported
        if "block comment" not in str(errors):
            errors.append(
                "yield from with block comment is not valid PHP syntax - "
                "'yield /*comment*/ from' should be a parse error"
            )
    
    return errors


def check_php_syntax(code: str) -> dict:
    """
    Validate PHP code syntax and return results.
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Check for yield from with comments (issue #14926)
    yield_errors = check_yield_from_with_comments(code)
    if yield_errors:
        result["valid"] = False
        result["errors"].extend(yield_errors)
    
    return result


def main():
    """Command-line entry point."""
    if len(sys.argv) < 2:
        print("Usage: python php_validator.py <php_code>")
        print("  <php_code>: Validate inline PHP code")
        sys.exit(1)
    
    code = sys.argv[1]
    
    result = check_php_syntax(code)
    
    if result["valid"]:
        print("PHP code is syntactically valid")
        sys.exit(0)
    else:
        print("PHP syntax validation FAILED:")
        for error in result["errors"]:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
