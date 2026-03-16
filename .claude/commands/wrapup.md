# End-of-Session Wrapup

Perform all end-of-session housekeeping:

1. Run tests and report results: `PYTHONPATH=. python -m pytest tests/ -v`
   (e2e browser tests excluded by default; use `-m ''` to include all)
2. Run lint: `ruff check templates/ tests/`
3. Append a dated entry to `docs/DEVLOG.md` with:
   - Date and session summary
   - What was accomplished (files changed, features added)
   - Decisions made and rationale
   - Blockers or open questions
   - Next steps
4. Verify all changes are committed
5. If on a feature branch, push and open a PR targeting `develop`
6. Print a final status summary

**Branching:** PRs target `develop`. Only merge `develop` → `main` for stable releases.
