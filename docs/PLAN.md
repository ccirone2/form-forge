# FormForge — Feature Plans

> Structured implementation plans for upcoming features.
> Branches are created from `develop`. Issues are linked to each task.

---

## Plan: Load Sample Data Button

**Goal:** Add a "Load Sample Data" button to the form submit area so users can instantly populate the form with representative data and export a demo DOCX without manual data entry.

**Status:** Planned (2026-03-10)

---

### Decision: Where does sample data come from?

Four options were considered:

| Option | Pros | Cons |
|--------|------|------|
| (a) Embedded in `index.html` | Zero network round-trips | Duplicates fixture data; grows the file |
| (b) Fetched from `tests/fixtures/{schemaName}_sample.json` | Fixtures already exist; single source of truth | Requires fixtures to be in the connected repo |
| (c) Schema-level `sampleData` property | Portable — travels with the schema | Adds schema verbosity; requires spec update |
| (d) Auto-generated from field definitions | Always available | Cannot produce realistic/representative data |

**Chosen approach:** (b) as primary, (c) as an optional fallback. Fetching fixtures reuses the existing `ghFetchRaw()` pattern with zero new infrastructure. The `sampleData` schema property covers repos that don't follow the fixture convention.

---

### Task 1 — Core: Load Sample Data button and fetch logic

**Issue:** #55
**Branch:** `feature/55-load-sample-data`
**Estimated effort:** ~1.5 hours

**Files modified:**
- `index.html`

**Changes:**
1. Add `currentSchemaName` state variable (string, set from schema file path on all 4 launch paths).
2. Add `loadSampleData()` async function:
   - Derives fixture path: `tests/fixtures/${currentSchemaName}_sample.json`
   - For GitHub paths: calls `ghFetchRaw(fixturePath)`, parses JSON, calls `populateForm(data, { skipFileFields: true })`
   - For local/demo paths (no `ghOwner`/`ghRepo`): shows toast "No sample data available for local or demo forms"
   - On 404 or parse error: shows toast "No sample data found for this form"
   - Logs all fetch attempts and outcomes
3. Add HTML button in `.submit-area` between Load Data and Reset:
   ```html
   <button class="btn-secondary" onclick="loadSampleData()">Load Sample Data</button>
   ```
4. Set `currentSchemaName` in all 4 launch paths:
   - `launchForm()` (GitHub): derived from `entry.schemaPath` (e.g., `schemas/onboarding.json` → `onboarding`)
   - GitHub picker `launchForm` override: same derivation
   - `launchLocal()`: derived from the schema filename if available, else `null`
   - `launchDemo()`: hardcoded to `null` (demo has no fixture in the repo)

**Deriving schemaName from schemaPath:**
```js
// entry.schemaPath = "schemas/onboarding.json"
const currentSchemaName = entry.schemaPath.replace(/^schemas\//, '').replace(/\.json$/, '');
// → "onboarding"
```

**Dependencies:** None (populateForm already handles all 17 field types with skipFileFields option)

**Tests:** Manual browser test — connect to `ccirone2/form-forge`, launch onboarding form, click Load Sample Data, verify all non-file fields populate. Also verify graceful failure for a form without a fixture file.

---

### Task 2 — Fixture coverage verification

**Issue:** #56
**Branch:** `feature/56-fixture-coverage`
**Estimated effort:** ~30 minutes

**Files modified:**
- `tests/fixtures/*.json` (verify existing; add any missing)
- `docs/SCHEMA_GUIDE.md`

**Changes:**
1. Verify the three existing fixture files match their schemas field-for-field.
2. Add a section to `SCHEMA_GUIDE.md` documenting the fixture naming convention and what values are required.
3. Add a CI-friendly check: `tests/test_schemas.py` can optionally assert that every `schemas/*.json` has a corresponding fixture (non-blocking warning or skipped test if file missing).

**Dependencies:** None (can be done independently of Task 1, but logical to do after)

---

### Task 3 — Schema-level `sampleData` fallback property

**Issue:** #57
**Branch:** `feature/57-schema-sample-data`
**Estimated effort:** ~1 hour

**Files modified:**
- `index.html` — `loadSampleData()` fallback branch
- `schemas/_schema.spec.json` — add optional `sampleData` object property
- `docs/SCHEMA_GUIDE.md` — document `sampleData`
- `tests/test_schemas.py` — validation tests

**Changes:**
1. `_schema.spec.json`: add `"sampleData": { "type": "object", "additionalProperties": { "type": "string" } }` as optional at schema root.
2. `loadSampleData()`: after a failed `ghFetchRaw`, check `currentSchema.sampleData`. If present, call `populateForm(currentSchema.sampleData, { skipFileFields: true })`.
3. `SCHEMA_GUIDE.md`: document `sampleData` with an example.
4. `test_schemas.py`: add `test_sampledata_optional` and `test_sampledata_validates` cases.

**Dependencies:** Task 1 (#55) must be merged first.

---

### Implementation Order

```
Task 1 (#55) ──▶ Task 3 (#57)
Task 2 (#56) ──▶ (independent, can merge anytime)
```

Both Task 1 and Task 2 can be opened as PRs simultaneously. Task 3 waits for Task 1 to land.

