# FormForge — Feature Plans

> Structured implementation plans for upcoming features.
> Branches are created from `develop`. Issues are linked to each task.

---

## Issue #40 — Improve Test Coverage

**Branch:** `feature/40-improve-test-coverage`
**Status:** In Progress

### Overview

Upgrade the test suite from smoke-only checks to meaningful content verification, add missing coverage paths, and modernize test patterns.

### Tasks (in order)

| # | Task | Files | Depends On |
|---|------|-------|------------|
| E | Refactor negative schema tests to `pytest.raises` | `tests/test_schemas.py` | — |
| B | Add duplicate field ID test across all schemas | `tests/test_schemas.py` | — |
| C | Add base64 image payloads to fixtures | `tests/fixtures/expense-report_sample.json`, `tests/fixtures/field-type-demo_sample.json` | — |
| A | Add round-trip DOCX content assertions | `tests/test_templates.py` | C |
| D | Add `visible_when` hidden-field path test | `tests/fixtures/field-type-demo_virtual_sample.json` (new), `tests/test_templates.py` | A |

### Task Details

**Task E — `pytest.raises` refactor**
Replace all 19 `try/except` + `assert False` blocks in negative schema tests with idiomatic `with pytest.raises(jsonschema.ValidationError)`. Pure mechanical refactor, no logic changes.

**Task B — Duplicate field ID check**
Add `_collect_all_ids(schema)` helper that walks sections → fields (including repeater sub-fields). Add `test_no_duplicate_field_ids` that iterates all schema files and asserts `len(ids) == len(set(ids))`.

**Task C — Base64 image fixtures**
Add a minimal 1x1 PNG data URI to:
- `expense-report_sample.json`: `receipt_photo` and `employee_signature`
- `field-type-demo_sample.json`: `applicant_signature`

**Task A — Round-trip content tests**
Add `_full_text(result)` helper that reads DOCX bytes back via `python-docx` and extracts all paragraph + table cell text. Add 3 new tests:
- `test_onboarding_content_round_trip` — verify `Alice`, `Johnson`, `Engineering`, `Senior Developer`
- `test_expense_report_content_round_trip` — verify `Jane Doe`, `Engineering`, `Flight to NYC`
- `test_field_type_demo_content_round_trip` — verify `Jane Doe`, `Conference`, `In-person`

**Task D — `visible_when` hidden path**
Create `field-type-demo_virtual_sample.json` with `attendance_mode=Virtual`, `virtual_platform=Zoom`, and empty strings for hidden fields. Add `test_field_type_demo_virtual_path` — assert `Zoom` appears, `100 Convention Center Dr` does not.

### Expected Result

| File | Tests Before | Tests After |
|------|-------------|------------|
| `test_templates.py` | 6 | 10 |
| `test_schemas.py` | 34 | 35 |
| `test_stencils.py` | 50 | 50 |
| **Total** | **90** | **95** |
