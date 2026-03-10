---
name: python-conventions
description: >
  Python coding conventions for the FormForge project. Apply when writing
  or editing any Python file in the templates/ or tests/ directory.
---

# Python Conventions for FormForge

## Type Hints
- All function signatures must have type hints
- Use `X | None` not `Optional[X]`
- Use `list[str]` not `List[str]` (Python 3.11+)
- Import `from __future__ import annotations` in all modules

## Docstrings (Google Style)
```python
def my_function(doc: Document, data: dict[str, str]) -> bytes:
    """Brief one-line summary.

    Longer description if needed.

    Args:
        doc: The python-docx Document instance.
        data: Field key-value pairs from the form.

    Returns:
        DOCX file bytes ready for download.

    Raises:
        ValueError: If data is invalid.
    """
```

## Module Structure
1. Module docstring
2. `from __future__ import annotations`
3. Standard library imports
4. Third-party imports
5. Local imports
6. Constants
7. Data classes
8. Private helpers
9. Public API functions
10. `if __name__ == "__main__":` CLI test block

## Pyodide Constraints
- No filesystem access (no open(), no Path.exists() in runtime code)
- No C extensions (use pure Python packages only)
- No threading/multiprocessing
- Use `io.BytesIO` for in-memory file operations
