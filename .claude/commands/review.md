# Code Review

Review the recent changes for quality and correctness.

1. Run `git diff develop --stat` to see what changed
2. For each modified file, check:
   - Type hints on all function signatures
   - Docstrings on all public functions
   - No raw `print()` in library code (only in `if __name__` blocks)
   - Pyodide compatibility (no filesystem, no C extensions, no threading)
   - Error handling (don't silently swallow exceptions)
   - Data round-trip safety (form data → DOCX export without loss)
3. Run tests: `PYTHONPATH=. python -m pytest tests/ -v`
   (e2e browser tests excluded by default; use `-m ''` to include all)
4. Check for any TODO/FIXME/HACK comments that should be issues
5. Provide a summary of findings

Focus area: $ARGUMENTS
