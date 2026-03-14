# FormForge Development Log

> A running journal of progress, decisions, and notes as the project evolves.

---

## How to Use This Log

- Add entries in reverse-chronological order (newest first)
- Each entry should include: date, related issue(s), what was done, and any decisions or rationale
- Keep entries concise but useful for future reference

---

## Log

### 2026-03-14 — UX: Custom Scrollbar Styling (#139)
**Issues:** #139

Added custom scrollbar styles to replace default browser scrollbars across all scrollable areas:

1. **Global dark scrollbars** — 6px thin scrollbars with `var(--border)` thumb, `var(--text-muted)` on hover, transparent track. Both WebKit (`::-webkit-scrollbar`) and Firefox (`scrollbar-width: thin`, `scrollbar-color`) supported.
2. **Dev Mode auto-fade** — Editor panes, preview panels, and error containers fade their scrollbar thumbs to transparent when not hovered, saving horizontal space in the split-pane layout.
3. **DOCX preview light scrollbar** — White-background preview uses light-gray scrollbar (`#ccc` / `#f5f5f5`) instead of dark theme colors.

Added 4 tests. Updated 1 existing test (`test_docx_preview_white_background_css`) to handle multiple CSS rule blocks.

**Decisions:**
- Used `var(--border)` for thumb (not accent) to keep scrollbars subtle and non-distracting
- 6px width balances visibility with minimal space usage
- Auto-fade only in Dev Mode panes where horizontal space is premium; other areas keep visible scrollbars

---

### 2026-03-14 — UX: Navigation & Organization Critique (#137)
**Issues:** #137

Design critique of the app's navigation and information architecture. Created issue #137 with five minor improvements:

1. Collapse documentation section behind a single accordion (separate form-filler vs form-creator content)
2. Auto-scroll to form picker after successful GitHub connection
3. Rename "Back to picker" → "Back" for consistency across all launch paths
4. Add double-click to launch on picker cards (zero-friction flow)
5. Add empty-state hint to profile dropdown

Also applied minor CSS cleanup: replaced remaining hardcoded transition values with design tokens (`--transition-base`, `--transition-slow`, `--transition-fast`) and added `focus-visible` outline to the Connect button.

**Decisions:**
- Documentation stays on the setup page but collapsed by default — avoids a separate view for a small amount of content
- "How It Works" card remains visible outside the accordion since it's useful context for all users

---

### 2026-03-14 — Dev Mode: Editor Enhancements (#130-#135)
**Issues:** #130, #131, #132, #133, #134, #135

Six enhancements to Dev Mode editors, improving the schema-to-template development workflow:

**Line Numbers & Code Folding (#130):**
- Added synchronized line-number gutters to all three editors (schema, template, sample data)
- Line numbers update on edit, scroll-synced with editor content
- Code folding for JSON `{}`/`[]` blocks and Python indented blocks (def, class, if, for, etc.)
- Fold indicators (▶/▼) in gutter, click to collapse/expand regions

**Keyboard Shortcuts (#131):**
- `Ctrl/Cmd+/` toggles `# ` comment prefix in Python editor (toast in JSON editors)
- `Alt+Up/Down` moves current line up or down
- `Ctrl+S` saves schema/template (workspace-aware, see #134)
- `Ctrl+Enter` runs DOCX preview in template builder
- Toolbar buttons show shortcut hints in title attributes

**Auto-Generated Sample Data (#132):**
- `SAMPLE_DATA_GENERATORS` maps all 23 field types to realistic placeholder values
- "Auto-fill" button in sample data panel generates JSON from current schema
- Auto-syncs on first use: when sample data is still `{}`, auto-fills on valid schema parse
- Repeater fields generate 2 sample rows recursively

**Schema-Template Cross-Awareness (#133):**
- Shared `devParsedSchema` state variable kept in sync with schema validation
- Template editor right-click menu gains "Schema Fields" submenu listing all fields with type-appropriate Python accessors (`data.get()`, `json.loads()`)
- Schema preview header shows coverage badge: "N/M fields used in template"

**Smart Save (#134):**
- `devSaveSchema()` and `devSaveTemplate()` check for active workspace before downloading
- If workspace connected and active file matches, saves to workspace via File System Access API
- Falls back to browser download otherwise

**Tests (#135):**
- 39 new tests covering all features (302 total in test_dev_mode.py, 430 total)

---

### 2026-03-14 — Dev Mode: GitHub Repo Integration in Workspace (#125)
**Issue:** #125

Added GitHub repository integration to the Dev Mode Workspace tab, completing the development loop: edit in Dev Mode, commit, push, forms are live.

**Connect Repo:**
- "Connect Repo" button in workspace toolbar alongside "Open Folder"
- Modal dialog with owner/repo input (accepts full GitHub URLs), PAT input (masked), and optional branch field
- Token stored in localStorage (`formforge-dev-github-token`) with clear button
- Security warning about token scope displayed in modal
- Fetches `schemas/*.json` and `templates/*.py` from connected repo via GitHub API
- Excludes `_schema.spec.json` and `stencils.py` as with local workspace
- Badge shows `owner/repo @ branch` with file count

**Commit & Push:**
- Commit button appears when files are modified in the builders
- Commit panel shows changed files summary and commit message textarea
- Single-file commits use GitHub Contents API (`PUT /repos/{owner}/{repo}/contents/{path}`)
- Multi-file commits use Git Trees + Commits API for atomic operations (blobs, tree, commit, ref update)
- 409 conflict detection with user-friendly error message
- Success toast with abbreviated commit SHA

**Branch Support:**
- Branch selector dropdown populated from GitHub API after connecting
- "New Branch" button creates a branch from current via `POST /repos/{owner}/{repo}/git/refs`
- Branch name validation (alphanumeric, dots, dashes, slashes)
- Switching branches re-fetches all files

**File Modification Tracking:**
- Original content stored on fetch for diff comparison
- Modified files tracked in `devGhModifiedFiles` Set
- Visual indicator (warning-colored dot) on modified files in file list
- Schema and template editor `onUpdate` hooks trigger modification tracking

**Other:**
- Disconnect button clears all GitHub workspace state and returns to empty workspace
- 3 new SVG icons: git-branch, git-commit, unlink
- All new CSS uses design tokens (no hard-coded values)
- 56 new tests covering HTML structure, CSS classes, SVG icons, JS functions, API patterns, and security

---

### 2026-03-14 — Dev Mode: Context menu end-to-end browser tests (#124)
**Issue:** #124

Added 24 Playwright-based end-to-end browser tests covering the right-click context menu in both the Schema Builder and Template Builder editors. These tests exercise runtime behavior that the existing static HTML tests in `test_dev_mode.py` cannot cover:

- **Schema Builder context menu:** menu appearance on right-click, 4 grouped submenus (Input/Choice/Complex/Layout), separator and action items (Add Section, Wrap in Wizard), field snippet insertion, unique ID generation on duplicate inserts, invalid JSON error toast, close on Escape and click-outside, live preview and validation badge updates.
- **Template Builder context menu:** menu appearance, stencils helper snippet items, snippet insertion into editor, close on Escape and click-outside.

Tests use a local HTTP server with OS-assigned port and a shared browser instance for efficiency. CodeJar loads as an ES module via dynamic `import()` in the app.

---

### 2026-03-13 — Dev Mode: Schema Builder, Template Builder & Local Workspace (#115)
**Issues:** #115 (#116, #117, #118, #119, #120, #121, #122)

Added a full Dev Mode with three tools for in-app form development:

**Schema Builder:**
- Split-pane editor with CodeJar + Prism.js JSON syntax highlighting
- Live form preview updates on 300ms debounce as schema is edited
- Real-time validation badge (valid/invalid/parse error) with error panel
- Right-click context menu with grouped field type snippets (Input/Choice/Complex/Layout)
- Insert section, wrap in wizard mode via context menu
- New/Load/Save/Format toolbar buttons

**Template Builder:**
- CodeJar + Prism.js Python syntax highlighting
- Collapsible sample data JSON editor
- "Preview DOCX" button runs template through Pyodide → mammoth.js HTML preview
- Right-click context menu with stencils helper snippets
- New/Load/Save toolbar buttons

**Local Workspace:**
- File System Access API for native folder picker with live 5s polling for external changes
- Drag-and-drop folder fallback via webkitGetAsEntry for cross-browser support
- Auto-discovers schemas/*.json and templates/*.py (excludes _schema.spec.json and stencils.py)
- Click-to-edit opens files in the appropriate builder tab

**Infrastructure:**
- Mode toggle button in header, persisted in localStorage
- Three-tab dev navigation (Schema Builder / Template Builder / Workspace)
- Draggable split-pane resizer with localStorage-persisted ratio
- Modified buildForm() to accept optional targetForm parameter for preview rendering
- Mobile gate: dev mode hidden on <768px, auto-exits on resize with toast

**CDN Dependencies:**
- Prism.js 1.29.0 (syntax highlighting, ~15KB)
- CodeJar 4.2.0 (lightweight code editor, ~5KB)
- mammoth.js 1.6.0 (DOCX to HTML conversion, ~70KB)
- DOMPurify 3.2.4 (HTML sanitization for mammoth output, ~7KB)

**Decisions:**
- All changes in index.html — no build step, no file splits
- CodeJar chosen over Monaco/CodeMirror for minimal footprint
- Prism theme overrides use existing design tokens for visual consistency
- Context menu inserts at schema level (appends to last section) rather than cursor position for reliability

---

### 2026-03-13 — Design Critique: UX, Microcopy, and Visual Polish (#109, #110, #111)
**Issues:** #109, #110, #111

Design critique and remediation focused on user experience, error messaging, feature discoverability, and visual consistency.

**Error Messages & Loading (#109):**
- Added `friendlyError()` helper mapping GitHub API errors (404, 401, rate limits) to human language
- Replaced all raw `err.message` toasts with contextual, actionable messages
- Replaced "Pyodide not ready" with "Export engine still loading — try again in a moment"
- Loading overlay now shows "may take 30–60 seconds on first load"
- Progress step labels renamed to user-friendly names
- Standardized toast punctuation (! for success, . for errors)
- Validation toast now shows count: "Missing 5 required fields: A, B, C and 2 more"

**Feature Discoverability (#110):**
- Profiles button tooltip explains autofill capability
- "Auto-saving" indicator with save icon added to form nav bar
- "Step X of Y" label added to wizard navigation
- Conditional fields now fade in with animation when revealed

**Visual Polish (#111):**
- Schema info banner text changed from accent to muted (reduced accent-on-accent noise)
- Added `--disabled-opacity` token replacing hard-coded opacity on disabled buttons
- Docs card h4 increased from 13px to 14px for better hierarchy
- List item removal now has exit animation (fade + slide)
- "Sample Data" button renamed to "Load Sample" for clarity

---

### 2026-03-13 — UI Audit: Design Tokens, Accessibility, and Polish (#103, #104, #105)
**Issues:** #103, #104, #105

Comprehensive UI audit and remediation across accessibility, theming, responsive design, and performance.

**Design Token Extraction (#103):**
- Expanded `:root` from 14 to 35+ CSS custom properties
- Added font families (`--font-sans`, `--font-mono`), type scale (`--text-2xs` through `--text-3xl`), radii (`--radius-xs` through `--radius-pill`), shadows, transitions
- Migrated all 47 font-family, ~110 font-size, ~45 border-radius, 4 box-shadow declarations to tokens
- Added `--text-on-accent`, 6 accent opacity variants, `--error-hover`, `--error-subtle`, `--success-subtle`
- Eliminated all hard-coded `rgba()` color values outside `:root`

**High-Impact Accessibility (#103):**
- Multi-select: ARIA combobox/listbox/option roles, keyboard nav (arrow keys, Enter, Escape)
- Form errors: `aria-invalid` + `aria-describedby` on inputs
- Address fields: proper `<label>` elements for all sub-inputs
- Profile dropdown: focus trap, `role="menu"`, Escape key, focus restoration
- Signature canvas: responsive CSS width + DPI-aware JS sizing
- Replaced `getImageData()` blank check with `hasDrawn` boolean flag

**Medium-Impact Accessibility (#104):**
- Views wrapped in `<main>` landmarks
- Loading overlay: `role="status"`, `aria-live`, `aria-busy`
- Autosave prompt: `role="alert"` + `aria-live="polite"`
- Wizard: full tablist/tab/tabpanel ARIA pattern
- Field errors: warning icon (⚠) via `::before` — not color-only
- Focus-visible rings on picker cards, wizard steps, docs headers
- Focus restoration after repeater row removal
- Address grid: 768px breakpoint for tablets

**Low-Impact Polish (#105):**
- Removed contrast-reducing opacity on longtext counter and list divider
- Added `aria-hidden` to decorative elements (status-dot, currency prefix)
- Refactored `<h1 role="button">` to semantic `<h1><button>`
- Branch input responsive fix for tablets
- `setTimeout(0)` → `requestAnimationFrame` for initial row creation

**Decisions:**
- SVG select chevron kept as data URI with sync comment (CSS-only approach too invasive)
- Responsive breakpoint sizes (26px, 22px, 17px) intentionally left as raw values (one-off overrides)

---

### 2026-03-11 — Add new field types: time, url, toggle, datetime, multi_select (#101)
**Issue:** #101

Added 5 new field types bringing the total from 18 to 23.

- **`time`** — Native time picker (`<input type="time">`), outputs `HH:MM` string. Column-pair type. Allowed in repeaters.
- **`url`** — URL input with browser validation (`<input type="url">`), outputs URL string. Column-pair type. Allowed in repeaters.
- **`toggle`** — Boolean yes/no switch, outputs `"true"`/`"false"`. Distinct from `checkbox` (multi-select). Column-pair type. Allowed in repeaters.
- **`datetime`** — Combined date+time picker (`<input type="datetime-local">`), outputs ISO-like string. Column-pair type.
- **`multi_select`** — Searchable multi-select dropdown with tag/chip UI, requires `options`. Outputs comma-separated string. Full-width type.

**Files changed:**
- `schemas/_schema.spec.json` — Updated `fieldType` and `repeaterFieldType` enums, all `allOf` constraint blocks
- `index.html` — CSS for toggle switch and multi-select; 5 new creator functions; `collectFormData`, `populateForm`, `isFieldEmpty`, column-pairing updates
- `schemas/field-type-demo.json` — Added all 5 new types to the demo schema
- `templates/field-type-demo.py` — Handle new types in DOCX generation
- `tests/fixtures/field-type-demo_sample.json` — Sample data for new fields
- `tests/test_schemas.py` — 9 new tests (positive + negative validation for new types, repeater eligibility)
- `docs/FIELD_TYPES.md`, `docs/SCHEMA_GUIDE.md`, `docs/TEMPLATE_GUIDE.md` — Documented all 5 types

**Decisions:**
- `time`, `url`, `toggle` allowed as repeater sub-fields (simple inputs); `datetime` and `multi_select` excluded (too wide/complex for repeater rows)
- `toggle` always has a value (`true`/`false`), so `isFieldEmpty` returns false — a required toggle always passes validation
- `multi_select` uses same comma-separated output format as `checkbox` for template compatibility

---

### 2026-03-11 — Responsive design polish for mobile and tablet (#89)
**Issue:** #89

Systematic responsive pass across all UI components for mobile and tablet viewports.

- **Tablet breakpoint (768px)** — Reduced header/container padding, form section and config card padding from 28px to 20px
- **Header (600px)** — Tighter padding (10px 12px), smaller title font, status badge shows dot only (text hidden)
- **Config cards** — `.config-row` stacks vertically on mobile; Connect button goes full-width
- **Form sections** — Padding reduced to 16px on mobile
- **Submit area** — All buttons stack vertically at full-width: export on top, secondary actions below, reset at bottom
- **Touch targets** — Remove-item, remove-row, profile delete/edit buttons, and token toggle all get 44x44px minimum tap targets on mobile
- **Profile dropdown** — Converts to bottom-sheet drawer on mobile (≤600px) with slide-up animation, full width, 70vh max height; JS positioning skipped in favor of CSS
- **Picker grid** — Single column on mobile
- **Local upload row** — Stacks vertically on mobile

**Decisions:**
- Used 768px for tablet, 600px for mobile, 400px for very narrow — consistent with existing breakpoints
- Profile delete/edit buttons always visible on mobile (no hover-to-reveal) for touch accessibility

---

### 2026-03-10 — Code quality: SVG icon reuse, event delegation, CSS organization (#92)
**Issue:** #92

Internal refactoring for maintainability — no user-facing behavior changes.

- **SVG sprite sheet** — Created a hidden `<svg>` sprite block at the top of `<body>` with 22 reusable `<symbol>` definitions. Replaced all inline SVG duplicates in HTML and JS `innerHTML` assignments with `<svg><use href="#icon-name"/></svg>` references.
- **Event delegation** — Replaced per-element event listeners with delegated handlers on parent containers for picker cards, list items, repeater row removes, and profile dropdown items.
- **CSS table of contents** — Added a 30-section numbered ToC at the top of `<style>` with corresponding section markers throughout.
- **Named constants** — Replaced magic numbers with `AUTOSAVE_SIZE_LIMIT`, `AUTOSAVE_DEBOUNCE_MS`, `TOAST_DURATION_MS`, and `DEFAULT_MAX_ROWS`.

---

### 2026-03-10 — Inline form validation with field-level error states (#84)
**Issue:** #84

Added inline validation with field-level error states to replace toast-only feedback.

- **Field-level error styling** — Invalid `.field-group` elements receive a `.field-error` class with red border, error glow, and inline error message.
- **Scroll to first error** — On validation failure, the first invalid field scrolls into view smoothly.
- **Validate on blur** — Required fields validate on blur for immediate feedback; errors clear on input/change.
- **Wizard validation gates** — `wizardNext()` and `wizardStepClick()` block forward navigation on validation failure.
- **ARIA** — Error messages have `role="alert"` for screen reader announcements.

---

### 2026-03-10 — Profile dropdown auto-focus refinement (#87)
**Issue:** #87

Refined profile dropdown UX to reduce friction when tabbing through form fields.

- **Guard on focus** — Dropdown only auto-shows when field is empty and profiles exist.
- **300ms debounce** — Quick tab-throughs no longer trigger the dropdown.
- **Dismissal tracking** — Dismissed fields (Escape/click-outside) won't reshow until page reload.
- **Profile icon indicator** — Added subtle person icon button at right edge of matching inputs as a manual trigger.
- **Listener guard** — Prevented accumulated mousedown listeners across form launches.

---

### 2026-03-10 — Loading states, error recovery, and progress feedback (#91)
**Issues:** #91

Improved UX around loading, errors, and progress feedback across the app:

- **Multi-step Pyodide progress indicator** — `initPyodide()` now shows a 3-step progress indicator (Pyodide runtime, Python runtime, python-docx) with numbered circles that light up as each phase completes, replacing the single static message.
- **Retry on failure** — Pyodide load failures now show a "Retry Loading Pyodide" button in the overlay instead of just a toast error. GitHub connect failures show an inline "Retry" button next to the error message.
- **Lazy Pyodide preloading** — `preloadPyodide()` fires silently in the background after DOMContentLoaded, so Pyodide is often already loaded by the time the user launches a form. Launch functions await the preload promise if one is running, showing "Preparing export engine..." in the overlay.
- **Parallel schema fetching** — `connectRepo()` now uses `Promise.all()` to fetch all schemas in parallel instead of sequentially in a for-loop.
- **Export progress feedback** — `handleExport()` now logs detailed progress to the console panel in real-time: field serialization, template execution timing (with `performance.now()`), and download preparation.

---

### 2026-03-10 — Keyboard shortcuts and navigation (#85)
**Issues:** #85

Added global keyboard shortcuts and improved keyboard accessibility for picker cards and the profile dropdown.

**Changes:**
- **Global keyboard shortcuts** (`index.html`): Added a `handleGlobalKeydown()` function registered in the BOOT section via `document.addEventListener('keydown', ...)`. Supports `Ctrl/Cmd+S` (save form data), `Ctrl/Cmd+Enter` (export to DOCX), and `Escape` (dismiss profile dropdown first, then navigate back to picker with a dirty guard confirmation). All shortcuts use `event.metaKey || event.ctrlKey` for cross-platform Mac/Windows support and call `event.preventDefault()` to override browser defaults.
- **Picker card keyboard navigation** (`renderPicker()`): Added `tabindex="0"`, `role="button"`, and `aria-label` attributes to each picker card. Added `keydown` listener so Enter/Space selects the card (same as click).
- **Profile dropdown keyboard navigation** (`showProfileDropdown()`): Added `tabindex="-1"` to each `.profile-dropdown-item` and a `keydown` listener on the dropdown container for ArrowUp/ArrowDown (cycle focus through items) and Enter (trigger click on focused item). Removed the standalone Escape keydown listener from `setupProfileDropdowns()` since the global handler now covers it.

**Decisions:**
- The Escape dirty guard uses `confirm()` to warn users about unsaved data before navigating back — checks both autosave storage and non-empty form fields
- Profile dropdown Escape is handled first (higher priority) before the back-to-picker action
- Dropdown items use `tabindex="-1"` (not `0`) so they are focusable programmatically via arrow keys but do not appear in the normal tab order

---

### 2026-03-10 — Quick UX wins: submit hierarchy, reset confirm, toast polish (#83)
**Issue:** #83

Batch of small, high-impact UX improvements in `index.html`:

- **Submit area button hierarchy** — Restructured the 5-button flat row into a clear visual hierarchy: Export to DOCX sits alone as the dominant primary CTA (larger, full-width accent), Save/Load/Sample Data are grouped in a secondary row below with smaller sizing, and Reset is right-aligned with a muted danger style that only shows color on hover.
- **Reset confirmation** — Added `confirm('Reset all fields? This cannot be undone.')` guard at the top of `resetForm()` to prevent accidental data loss.
- **Toast improvements** — Added `role="alert"` and `aria-live="polite"` to the toast element for screen reader announcements. Added a dismiss button (x) so users don't have to wait 3.5s. Added mobile-responsive positioning (centered bottom bar on narrow screens via `@media (max-width: 600px)`). Added `warning` border-color style for warning toasts.
- **Inline styles cleanup** — Extracted ~15 inline `style="..."` attributes into proper CSS classes: `.demo-btn-wrapper`, `.btn-demo`, `.section-label-muted`, `.config-card-description`, `.local-launch-row`, `.branch-input-wrapper`, `.docs-source-divider`, `.how-it-works-card`, `.how-it-works-description`, `.how-it-works-pre`, `.icon-inline`, `.hidden-input`, `.docs-rendered-md-link`. Only `style="display:none;"` on the JS-toggled pickerSection remains as inline.

All 95 tests pass.

---

### 2026-03-10 — Navigation guards for unsaved form data (#86)
**Issue:** #86

Added dirty-state tracking and navigation guards to prevent accidental data loss:

- **`formDirty` flag** — New state variable tracks whether the form has unsaved changes. Set `true` on any `input`/`change` event (via the existing autosave handler in `setupAutosave()`) and on `populateForm()` calls (load data, sample data, autosave restore). Reset to `false` after successful export, save data, form reset, and on fresh form launch (via `postLaunchHook()`).
- **In-app navigation guard** — `showView()` now checks `formDirty` when navigating from the form view back to setup. Prompts the user with a confirm dialog before discarding changes. Protects both the "Back to picker" button and the FormForge logo click.
- **Browser unload guard** — Added `beforeunload` handler that prevents browser close/refresh/back when the form has unsaved changes.
- **Reset confirm** — `resetForm()` now prompts the user before clearing the form if there are unsaved changes.

All 95 tests pass (frontend-only changes).

---

### 2026-03-10 — Improve test coverage: round-trip assertions, edge cases, visible_when paths (#40)
**Issues:** #40

Upgraded the test suite from smoke-only checks to meaningful content verification, added missing coverage paths, and modernized test patterns. Test count: 90 → 95.

**Changes:**
- **`tests/test_schemas.py`:** Refactored all 19 negative tests from `try/except` + `assert False` to idiomatic `pytest.raises`. Added `_collect_all_ids()` helper and `test_no_duplicate_field_ids` test that validates unique field IDs across all sections (including repeater sub-fields) in every schema.
- **`tests/test_templates.py`:** Added `_full_text()` helper that reads DOCX bytes back via `python-docx` and extracts all paragraph + table cell text. Added 3 round-trip content tests (`test_onboarding_content_round_trip`, `test_expense_report_content_round_trip`, `test_field_type_demo_content_round_trip`) that verify actual field values appear in generated documents. Added `test_field_type_demo_virtual_path` that exercises the `visible_when` hidden-field path (Virtual attendance mode).
- **`tests/fixtures/expense-report_sample.json`:** Added 1x1 PNG base64 data URI to `receipt_photo` and `employee_signature` fields.
- **`tests/fixtures/field-type-demo_sample.json`:** Added 1x1 PNG base64 data URI to `applicant_signature` field.
- **`tests/fixtures/field-type-demo_virtual_sample.json`:** New fixture with `attendance_mode=Virtual`, `virtual_platform=Zoom`, and empty strings for hidden fields (`venue_address`, `dietary_restrictions`).
- **`docs/PLAN.md`:** Added implementation plan for issue #40.

**Decisions:**
- Used a minimal 1x1 PNG (~120 chars) for base64 fixtures to keep files small while exercising the image embed code path
- Kept existing smoke tests (valid ZIP checks) alongside new content tests — they cover different failure modes
- `_full_text()` scans both paragraphs and table cells since `table_section()` writes to table cells, not standalone paragraphs

---

### 2026-03-10 — User profile autofill: inline dropdown with multi-profile support (#73, #74, #75)
**Issues:** #73, #74, #75

Redesigned the user profile autofill from a modal+banner approach to an inline on-focus dropdown with multi-profile support. All management is done inline — no modal needed.

**Changes (all in `index.html`):**
- **CSS (~100 lines):** `.profile-btn` with badge counter, `.profile-dropdown` (fixed-positioned card with shadow), `.profile-dropdown-item` (hover-reveal edit/delete buttons), `.profile-filled` (subtle purple highlight for auto-filled fields), `.profile-editor` (inline editor within dropdown)
- **HTML:** "Profiles" nav button with badge, single shared `<div class="profile-dropdown">` container
- **JS (~350 lines):**
  - **Multi-profile storage:** `getProfiles()` / `saveProfiles()` / `addProfile()` / `deleteProfile()` — array in localStorage under `formforge_user_profiles`, with migration from old single-profile format
  - **Auto-naming:** `getProfileDisplayName()` derives name from `name`, `first_name`+`last_name`, or `email`
  - **Field matching:** `PROFILE_MATCHERS` (type+label regex for 8 keys including job_title), `getMatchedProfileKey()` tests a single field
  - **Dropdown:** `showProfileDropdown()` renders profile items with field-specific preview values, edit/delete buttons, and "Save current form as profile" action. Positioned via `getBoundingClientRect()` with viewport overflow correction
  - **Profile editor:** `showProfileEditor()` renders inline editor within dropdown for viewing/editing all profile fields (name, email, phone, department, job title, address)
  - **Apply:** `applyProfileToForm()` fills all matched empty fields, adds `.profile-filled` highlight class, attaches one-time input listener to clear highlight on user edit
  - **Collect:** `collectProfileFromForm()` reverse-matches form fields to build a profile object
  - **Nav button:** `toggleProfileNav()` opens dropdown showing all profiles with edit/delete actions
  - **Field focus:** `setupProfileDropdowns()` attaches focus handlers to all matched fields
  - **Dismiss:** Global mousedown + Escape key listeners

**Profile fields (matched via type + label regex):**
`first_name`, `last_name`, `name`, `email`, `phone`, `department`, `job_title`, `address`

To add a new profile field: add entry to `PROFILE_MATCHERS` and `PROFILE_FIELD_LABELS` (~line 3040).

**UX flow:**
1. Fill form fields → click any matched field → dropdown appears with "Save current form as profile"
2. On next visit, click any matched field → dropdown shows saved profiles with field-specific preview
3. Click a profile → all matched empty fields are filled with purple highlight, toast shows count
4. Highlight clears when the user manually edits a field
5. Nav "Profiles" button shows all profiles for management (edit/delete)
6. Edit button opens inline editor with all profile fields

---

### 2026-03-10 — Plan: User Profile Autofill (#73 → #74–#75)
**Issues:** #73, #74, #75

Planned a localStorage-based "My Profile" feature to reduce duplicate data entry across forms. Users save personal info (name, email, phone, address, department) once, and matching fields are auto-detected and offered for autofill on form load.

**Tasks:**
- **#74** — Profile modal UI and localStorage CRUD (CSS, HTML, JS for editor modal + persistence)
- **#75** — Field matching engine and autofill prompt (type+label heuristics, banner UI, integration with postLaunchHook/resetForm)

**Decisions:**
- User Profile only (no schema-level `autofill_from` linking for now)
- Match fields using dual criteria: field type + label regex — avoids false positives
- Only fill empty fields — never overwrite autosave-restored or manually entered data
- Profile banner appears after autosave restore to respect the restore flow
- All changes in `index.html` only — no schema spec or test changes needed

---

### 2026-03-10 — Refactor index.html for maintainability (#38 → #68–#71)
**Issues:** #38, #68, #69, #70, #71

Implemented all 4 sub-tasks of the refactor:

- **#68 Eliminate monkey-patching** — Merged the duplicate `launchForm` (line 3230 override → single definition at line 1480). Inlined `loadDocs()` call directly into `connectRepo()` body, removing `_origConnectRepo` monkey-patch. Removed `_originalLaunchForm` and `_origConnectRepo` variables.
- **#69 Unify validation** — Extracted shared `validateSection(section)` that validates directly from the DOM with explicit radio, checkbox, and address branches. Both `wizardValidateStep()` and `validateForm()` now delegate to it. Fixes divergence where `validateForm` previously lacked radio/checkbox-specific validation.
- **#70 Extract createField** — Decomposed the 416-line `createField()` into 16 named creator functions (`createTextField`, `createDateField`, etc.) registered in a `fieldCreators` map. `createField()` is now a 28-line dispatcher handling labels, delegation, and hints.
- **#71 Update CLAUDE.md** — Replaced the "touches three places" bullet with a complete 6-item checklist covering all actual touch points for adding a new field type.

**Net result:** index.html reduced from 3270 → 3234 lines (−36). All 90 tests pass.

---

### 2026-03-10 — Miscellaneous cleanup (#43 → #61–#66)
**Issues:** #43, #61, #62, #63, #64, #65, #66

Implemented all 6 sub-tasks of the miscellaneous cleanup:

- **#61 Token masking** — Changed `tokenInput` from `type="text"` to `type="password"` so GitHub tokens are masked while typing.
- **#62 Event listener stacking** — Split `setupConditionalVisibility()` into three functions: `setupConditionalVisibility()` (attaches listeners + evaluates, called only from `buildForm()`), `evaluateAllConditionals()` (re-evaluates without attaching listeners, called from `populateForm()` and `resetForm()`), and `_buildConditionalDependencies()` (shared dependency map builder). Fixes memory leak where N populates caused N copies of evaluate handlers.
- **#63 Schema spec fixes** — Changed `min`/`max` from `"type": "integer"` to `"type": "number"` in both `field` and `repeaterField` definitions (allows float constraints like `0.5`). Added `allOf` exclusion rules to `repeaterField`: `min`/`max`/`step` restricted to `number`, `currency_symbol` restricted to `currency`, `maxLength` restricted to `text`. 5 new schema tests (90 total).
- **#64 Field type count** — Updated all references from "17" to "18" in SCHEMA_GUIDE.md, README.md, CLAUDE.md, field-type-demo.py, and field-type-demo.json.
- **#65 Type hints** — Added `from __future__ import annotations` and type annotations to all public and private function signatures in `stencils.py` (16 functions). Added `generate_docx(data: dict[str, str]) -> bytes` to all 3 templates.
- **#66 Configurable fallback URL** — Extracted the hardcoded `stencils.py` fallback URL into a `FORMFORGE_FALLBACK` constant (`{ owner, repo, branch }`) in the state section. URL is now derived from the constant via template literal.

---

### 2026-03-10 — Plan: Miscellaneous cleanup (#43 → #61–#66)
**Issues:** #43, #61, #62, #63, #64, #65, #66

Reviewed issue #43 (created 2026-03-04) for current relevancy. 6 of 8 original items are still applicable; 1 partially relevant (URL renamed from `_base.py` to `stencils.py`), 1 fixed (mid-function imports in `onboarding.py`). Updated issue body to reflect current state.

Broke #43 into 6 independent tasks:
- **#61** — Token input masking: `type="text"` → `type="password"` (bug, trivial)
- **#62** — Event listener stacking in `setupConditionalVisibility` (bug, moderate)
- **#63** — Schema spec: `min`/`max` accept floats + `repeaterField` exclusion rules (bug, moderate)
- **#64** — Update field type count from "17" to "18" in all docs (documentation, trivial)
- **#65** — Python type hints on all public function signatures (enhancement, moderate)
- **#66** — Extract hardcoded stencils.py fallback URL to configurable constant (enhancement, low)

All tasks are independent with no ordering constraints.

---

### 2026-03-10 — Wizard step indicator: clickable navigation + mobile responsive
**Issues:** #59

- **Clickable step circles** — Each wizard step in the indicator bar is now clickable. Navigation to any step is unrestricted — no intermediate validation on click. Validation still occurs at submit time.
- **Checkmark icons** — Completed steps display a checkmark SVG instead of the step number, providing clear visual progress feedback.
- **Hover effects** — Steps scale up slightly on hover with accent border color. Active step suppresses the scale to avoid visual jitter.
- **Mobile responsive (≤600px)** — Step labels are hidden, circles shrink to 28px, connectors to 24px with tighter margins.
- **Small screen (≤400px)** — Circles shrink further to 24px, connectors to 16px.
- **Touch-friendly** — Added `touch-action: manipulation` to prevent double-tap zoom delay, `padding: 6px 0` for larger hit area.
- **Keyboard accessible** — Steps have `role="button"`, `tabindex="0"`, and respond to Enter/Space keys.

### 2026-03-10 -- DOCX styling and layout polish

- **Title & Heading 1 horizontal rules** — Added bottom borders (`w:pBdr`) to Title and Heading 1 styles using `color_subtitle` for theme-matched lines.
- **Heading spacing** — 6pt `space_after` on Heading 1, 4pt on Heading 2–6.
- **Bullet list indent fix** — `bullet_list()` now overrides the numbering-level indent via XML (`w:left="720" w:hanging="360"`) instead of `paragraph_format.left_indent` which was ignored by Word's numbering definition. Bullet at 0.25", text at 0.5".
- **Table section left margin** — First column cells get 0.25" left margin via `_set_cell_left_margin()`.
- **Theme contrast for print** — Darkened `color_muted` and `color_footer` across all three themes for WCAG AA compliance and print reliability:
  - Classic: muted #999→#767676, footer #AAA→#6B6B6B
  - Minimal: subtitle #555→#4A4A4A, muted #AAA→#6B6B6B, footer #CCC→#595959
  - Modern: subtitle #4A8FA3→#3A7A8C, muted #8FA9B2→#5A7A85, footer #B0C4CB→#4D6E78
- **Theme margins** — All themes now use 0.75" bottom margin and 1.0" left/right.
- **Cache-busters** — GitHub raw fetches append `?t=` timestamp to prevent stale responses.
- **Wizard navigation** — Removed step-locking so users can freely navigate between wizard steps.
- New tests: `test_bullet_list_indent`, `test_table_section_first_column_has_left_margin`.

---

### 2026-03-10 -- Load Sample Data button + sampleData schema property (#55, #56, #57)
**Issues:** #55, #56, #57

- **Load Sample Data button** added to the submit area alongside Save Data / Load Data. Clicking it fetches `tests/fixtures/{schemaName}_sample.json` from the connected GitHub repo via `ghFetchRaw()`, then calls `populateForm(data, { skipFileFields: true })`.
- **`currentSchemaName` state variable** added and set in all 4 launch paths (GitHub launchForm, picker override, launchLocal, launchDemo). Derived from the schema file path by stripping `schemas/` prefix and `.json` suffix. Empty string for local/demo paths.
- **Fallback to inline `sampleData`** — if no fixture file is found (404 or no connected repo), `loadSampleData()` checks `currentSchema.sampleData` and uses it directly. Added `sampleData` to `DEMO_SCHEMA` so the demo form works without a GitHub connection.
- **`sampleData` schema property** — added optional `sampleData` object to `_schema.spec.json`. Allows schemas to ship inline sample data for repos without fixture files.
- **3 new schema tests** (83 total): `test_sample_data_validates`, `test_sample_data_is_optional`, `test_rejects_sample_data_non_object`.
- **SCHEMA_GUIDE.md** updated with Sample Data section documenting fixture naming convention and inline `sampleData` fallback.
- All 3 existing fixture files verified complete for their schemas.
- **Heading bold fix** — Added `_clear_bold()` helper that sets both `w:b` and `w:bCs` to `val="0"` on heading styles. Word's built-in headings carry `<w:bCs/>` (bold complex script) which renders bold even when `w:b` is disabled. Applied to Title and Heading 1-6. Consolidated the two heading loops into one.
- **Table cell margins** changed from 0.02" to 0.03" on all tables.

**Decisions:**
- Fixture file takes precedence over inline `sampleData` — single source of truth for test suite and UI.
- `skipFileFields: true` passed to `populateForm` since fixture files use empty strings for file/signature fields.
- Local/demo paths set `currentSchemaName = ''` so the fixture fetch is skipped cleanly; they fall through to the `sampleData` check or show a toast.

---

### 2026-03-10 -- Plan: Load Sample Data button (#55, #56, #57)
**Issues:** #55, #56, #57

Planned a feature to add a "Load Sample Data" button alongside the existing Save Data / Load Data buttons in the form submit area. The button lets users instantly populate the form with representative fixture data so they can export a demo DOCX without manual input.

**Decision: fetch from tests/fixtures/ as primary source.** Four approaches were considered (embedded in index.html, fetched from fixtures, schema-level sampleData property, auto-generated). Fetching tests/fixtures/{schemaName}_sample.json via the existing ghFetchRaw() utility is the simplest path -- the three fixture files already exist and cover all current schemas, and it avoids duplicating data inside index.html.

**Decision: schema-level sampleData as optional fallback.** For repos that do not follow the fixture convention, a sampleData property in the schema JSON can supply inline sample values. This is optional and requires a _schema.spec.json update and schema validation tests.

**Three tasks planned:**
- **Task 1 (#55):** Core button + loadSampleData() function in index.html. Adds currentSchemaName state variable set across all 4 launch paths. ~1.5h.
- **Task 2 (#56):** Fixture coverage verification and SCHEMA_GUIDE.md documentation of the fixture naming convention. ~30 min.
- **Task 3 (#57):** sampleData schema property as fallback; spec update, tests, docs. Depends on #55. ~1h.

Implementation order: Task 1 and Task 2 are independent. Task 3 waits for Task 1.

---

### 2026-03-10 — DOCX styling fixes: fonts, headings 3-6, spacing, tables

- **Theme font override fix** — Added `_set_style_font()` helper that strips `w:asciiTheme`/`w:hAnsiTheme`/`w:cstheme`/`w:eastAsiaTheme` attributes from built-in Word styles (Title, Heading 1-6, Subtitle, List Bullet, Normal). Without this, Word's theme-linked font references silently override `python-docx`'s `style.font.name`, causing Calibri to render instead of Segoe UI.
- **Heading 3-6 support** — Added `size_heading3` (12pt), `size_heading4`/`5`/`6` (11pt) to `DocTheme` dataclass and all three themes. Configured in `_build_template()` with heading font, theme colors, and `bold = False`.
- **Normal style spacing** — Set `space_after = Pt(0)` on the Normal style (was defaulting to 10pt).
- **Table cell margins** — Added `_set_cell_margins()` helper; applied 0.02" top/bottom margins to all tables (table_section, signatures, repeater_table).
- **Repeater table borders** — Changed from full grid borders to horizontal-only (top, bottom, insideH); vertical borders (left, right, insideV) set to none.
- **Repeater header bold** — Added `r.bold = True` on header row runs for proper semibold rendering.
- **Color field rename** — Renamed `title`/`subtitle`/`muted`/`footer`/`accent` to `color_title`/`color_subtitle`/`color_muted`/`color_footer`/`color_accent` across DocTheme, all themes, stencils.py usage sites, and tests.
- **THEME_MODERN margins** — Updated to bottom=0.75", left/right=1.5".
- All 80 tests pass.

---

### 2026-03-10 — Implement DocTheme + cached template + manual table styling (#53)
**Issues:** #53

Replaced the piecemeal styling system (Palette + font constants + per-run overrides + built-in Word table styles) with a unified `DocTheme` system:

- **`DocTheme` frozen dataclass** with 21 fields: 5 colors, 3 fonts, 8 sizes, 4 page margins. Replaces `Palette` (5 colors only) + `FONT_BODY/HEADING/CAPTION` constants + hardcoded sizes.
- **3 built-in themes:** `THEME_CLASSIC`, `THEME_MODERN`, `THEME_MINIMAL` — drop-in replacements for the old `PALETTE_*` constants.
- **Programmatic DOCX template** built once per theme at first use, cached as bytes. `_build_template()` creates a Document, strips all table styles except Normal Table, pre-configures 6 paragraph styles (Title, Heading 1, Heading 2, Subtitle, List Bullet, Normal) with theme colors/fonts/sizes, sets page margins, clears body content, and serializes to bytes. `new_doc()` clones from cache via `Document(io.BytesIO(cached_bytes))`.
- **Manual table XML formatting** via `_set_table_borders()` and `_shade_cells()` helpers — bypasses python-docx's buggy table style API. Key-value tables are borderless; repeater tables get grid borders with shaded headers.
- **Updated all templates** (`onboarding.py`, `expense-report.py`, `field-type-demo.py`) from `set_palette()`/`PALETTE_*` to `set_theme()`/`THEME_*`.
- **Rewrote index.html demo template** from ~120 self-contained lines to ~55 lines using stencils helpers.
- **80 tests** (up from 70): new tests for template builder (valid bytes, style stripping, style configuration, margins, cache), table XML assertions (borderless, grid, header shading), and theme system.
- **Updated `TEMPLATE_GUIDE.md`** — replaced "Color palettes" with "Document themes", updated `new_doc` signature, table descriptions, and examples.

**Decisions:**
- Template cache keyed by frozen DocTheme instance (hashable because all fields are hashable) — different themes get different cached templates.
- Stripping table styles at build time (not runtime) eliminates Word's theme engine auto-applying accent colors from the ~100 embedded table style definitions in python-docx's default template.
- Title rendered as `add_heading(level=0)` using the pre-configured Title style, not manual run formatting — style inheritance means `run.font.color.rgb` returns `None` (tests check style, not run).

---

### 2026-03-10 — Plan: DocTheme + cached template + manual table styling (#53)
**Issues:** #53

Investigated why DOCX tables render with Word's "Light Grid Accent 1" style despite explicit style assignments. Root cause: `python-docx`'s default `Document()` template embeds ~100 table style definitions in `styles.xml` that Word's theme engine resolves with accent colors.

Broader problem: formatting is scattered — colors in Palette, fonts as module constants, sizes hardcoded per-function, heading styles overridden per-run, page layout never set. Not extendable.

**Decision:** Replace `Palette` + font constants + per-run overrides with a unified `DocTheme` dataclass (colors, fonts, sizes, page layout). Build a fully-styled DOCX template programmatically at import time, cache as bytes, clone in `new_doc()`. Table formatting via direct XML helpers (python-docx table style API has known bugs). 4 phases: core infrastructure, stencils refactor, consumer updates (templates + index.html demo), tests & docs.

Abandoned prototype branch `feature/manual-table-styling`.

---

### 2026-03-10 — Named Color Palettes for stencils.py (#48–#51)
**Issues:** #48, #49, #50, #51

Added a palette system to `stencils.py` with 3 built-in palettes and custom palette support:

- **`Palette` dataclass** with 5 semantic roles: `title`, `subtitle`, `muted`, `footer`, `accent`
- **3 built-in palettes:** `PALETTE_CLASSIC` (bold navy/blue — default, preserves existing colors), `PALETTE_MINIMAL` (near-monochrome, extremely restrained), `PALETTE_MODERN` (contemporary teal/slate)
- **`set_palette(palette)`** — switches the active palette for all subsequent stencils calls; raises `ValueError` on incomplete palettes
- **`new_doc(palette=)`** — optional per-document palette override for title/subtitle colors without mutating global state
- **Wired all 9 helper functions** to read from `_active_palette` instead of hardcoded constants
- **Removed legacy `COLOR_*` module constants** (`COLOR_DARK_NAVY`, `COLOR_MEDIUM_BLUE`, `COLOR_SOFT_BLUE`, `COLOR_MUTED`, `COLOR_LIGHT_MUTED`) — all color access now goes through the palette system exclusively
- **11 new tests** covering palette existence, role matching, switching, restoration, invalid palettes, custom palettes, and `new_doc()` overrides (70 total)
- **Updated `TEMPLATE_GUIDE.md`** — rewrote "Color palette" section to document palettes, `set_palette()`, `new_doc(palette=)`, and custom `Palette` construction

**Decisions:**
- Used `dataclass(frozen=True)` for `Palette` to make palettes immutable and hashable
- Default palette is `PALETTE_CLASSIC` — existing templates produce identical output with zero changes
- Removed legacy `COLOR_*` constants entirely rather than keeping them as aliases — cleaner API, no backward compatibility needed
- `new_doc(palette=)` is intentionally scoped to title/subtitle only; use `set_palette()` for full-document palette control

---

### 2026-03-10 — Rename `_base.py` → `stencils.py` and Shorten Function Names

- Renamed `templates/_base.py` to `templates/stencils.py`
- Renamed `tests/test_base.py` to `tests/test_stencils.py`
- Dropped `add_` prefix from all helper functions: `add_table_section` → `table_section`, `add_longtext` → `longtext`, `add_bullet_list` → `bullet_list`, `add_signatures` → `signatures`, `add_footer` → `footer`, `add_address_block` → `address`, `add_image_or_placeholder` → `image`, `add_signature_line` → `signature`, `add_repeater_table` → `repeater_table`; `new_doc` and `finalize` unchanged
- Updated all call sites in 3 template files, test files, `index.html` (Pyodide loader), `CLAUDE.md`, `README.md`, and `docs/TEMPLATE_GUIDE.md`
- All 59 tests pass, linting clean

**Decisions:**
- `stencils` is a more descriptive module name than the underscore-prefixed `_base`
- Shorter function names (`stencils.footer(doc)` vs `_base.add_footer(doc)`) reduce verbosity since the module name already provides context

---

### 2026-03-04 — Keyboard Accessibility for Interactive Elements (#42)
**Issues:** #42

- **Clickable non-interactive elements** (`<h1>` logo, console header, 4 docs card headers) now have `tabindex="0"`, `role="button"`, and `onkeydown` handlers for Enter/Space.
- **Collapsible sections** (docs cards + console) toggle `aria-expanded` on open/close via `toggleDocs()` and `toggleConsole()`. Docs headers also have `aria-controls` pointing to their content panel.
- **Checkbox/radio groups** now have `role="group"` and `aria-labelledby` pointing to their group label `<span>` (given a unique `id`).
- **Signature canvas** has `aria-label="Signature pad — draw your signature with mouse or touch"`.

**Decisions:**
- Used `role="group"` + `aria-labelledby` instead of `<fieldset>`/`<legend>` to avoid CSS reset issues with the existing dark-theme styling.

---

### 2026-03-04 — CI Improvements: Ruff Linting, Dependency Pins, Cleanup (#41)
**Issues:** #41

- **Added `ruff check` lint step** to CI workflow — catches lint issues before merge.
- **Created `requirements-dev.txt`** with version-bounded dependencies: `python-docx>=1.1,<2`, `jsonschema>=4.23,<5`, `pytest>=8,<9`, `ruff>=0.4,<1`. CI now installs from this file.
- **Removed redundant inline schema validation** step from CI — this duplicated `test_schemas.py::test_validate_all_schemas` with worse error reporting.
- **Added pip caching** via `actions/cache@v4` keyed on `requirements-dev.txt` hash.

**Decisions:**
- Used version ranges (not exact pins) to allow patch updates while preventing breaking major/minor changes.

---

### 2026-03-04 — Extract Duplicated Template Patterns into _base.py (#39)
**Issues:** #39

Consolidated duplicated template code into shared `_base.py` utilities and fixed bugs:

- **`add_footer(doc)`** — Standard auto-generated footer. Replaced 3 identical footer blocks (onboarding, expense-report, field-type-demo). Also removed mid-function imports in onboarding.py.
- **`add_address_block(doc, heading, raw_json)`** — Parses address JSON and renders formatted block. Fixes the empty-city bug (`, ST ZIP` → `ST ZIP`). Replaced 2 duplicate blocks.
- **`add_image_or_placeholder(doc, b64_str, width_inches, placeholder)`** — Base64 image embed with graceful fallback. Replaced 3 duplicate blocks.
- **`add_signature_line(doc, b64_str, label, width_inches)`** — Signature image or underline placeholder with label. Replaced 3 duplicate blocks.
- **`add_repeater_table(doc, headers, items, field_keys, currency_keys)`** — Repeater field as a headed table with optional currency formatting. Replaced 2 duplicate blocks.
- **Truthiness fix** in `add_table_section`: `"0"` and `0` now render as `"0"` instead of an em dash.
- **Narrowed exception handlers** from bare `except Exception` to `(ValueError, binascii.Error, OSError, UnrecognizedImageError)`.
- **13 new tests** for all new utilities, edge cases (empty city, invalid base64, zero values), bringing total to 59.

**Decisions:**
- `expense-report.py` no longer imports `io`, `base64`, `Inches`, `Pt`, `WD_ALIGN_PARAGRAPH`, or `WD_TABLE_ALIGNMENT` — all handled by `_base`.
- `field-type-demo.py` still imports `Pt` for inline text formatting that doesn't use a `_base` utility.
- Address formatting builds city/state/zip from non-empty parts rather than f-string interpolation with empty guards.

---

### 2026-03-04 — Critical Bug Fixes: XSS, Repeater Populate, Fixtures, Docs (#37)
**Issues:** #37

Fixed four critical issues identified during deep code review:

- **XSS via unsanitized innerHTML** — Applied `escapeHtml()` to all GitHub-fetched values in `renderPicker()` (schema icon, name, description) and both `schemaInfoText` assignments (schema/template paths). Also sanitized markdown link URLs in `inlineFormat()` to reject `javascript:` protocol — only `http://` and `https://` URLs are now emitted as href values.
- **Silent repeater population failure** — `populateForm()` used selector `.btn-add-row` but the actual repeater add button class is `.btn-add-item`. Repeater data silently failed to restore from save/load and autosave. Fixed the selector.
- **Fixture data mismatch** — `onboarding_sample.json` had `laptop_preference: "MacBook Pro"` (not a valid schema option; corrected to `"MacBook Pro 14\""`) and `equipment_needs` used `\n` separator (checkbox fields serialize with `, `; corrected to `"External Monitor, Mechanical Keyboard"`).
- **Doc contradiction on maxLength** — `SCHEMA_GUIDE.md` claimed `maxLength` "displays a live counter" for all types. In reality, only `longtext` has a counter; `text` uses `maxLength` for schema validation only. Corrected the description.

**Decisions:**
- Used `escapeHtml()` rather than switching to `textContent` to preserve existing HTML structure in picker cards
- Sanitized markdown links to http/https only (no `data:`, `javascript:`, etc.)

---

### 2026-03-04 — Form Data Save/Load & Autosave (#29–#35)
**Issues:** #29, #30, #31, #32, #33, #34, #35

Added complete data persistence lifecycle to FormForge:

- **`populateForm(data, options)`** (#29) — Inverse of `collectFormData()`. Restores all 17 field types from a `{fieldId: stringValue}` dict, including radio, checkbox, list, address (JSON), repeater (JSON), file (with image preview), signature (drawn onto canvas), and longtext (with character counter update). Re-evaluates `visible_when` rules after populate. Warns on mismatches without blocking.
- **Save Data button** (#30) — Downloads current form data as `{title}_data_{date}.json` with `_formforge` metadata (schemaTitle, savedAt, version).
- **Load Data button** (#31) — Uploads a saved `.json` file, validates JSON, warns on schema mismatch, and calls `populateForm()` to restore fields.
- **localStorage autosave** (#32) — Debounced (2s) autosave on input/change, per-schema keys, large-field skipping (>50KB), restore prompt banner with "Restore" / "Discard" buttons, cleared on export and reset.
- **URL parameter loading** (#33) — `?data=<url>` fetches and populates form data after launch. Takes precedence over autosave restore.
- **`postLaunchHook()`** (#34) — Shared hook called after all 4 launch paths (local, demo, GitHub, picker) that wires up autosave and URL/autosave restore.
- **UI changes** (#35) — Save Data / Load Data buttons with Feather-style SVG icons in submit area. Autosave prompt banner CSS with warning accent and fade-in animation. Responsive layout.

**Decisions:**
- `_formforge` metadata key uses underscore prefix to avoid collision with field IDs (which must start with `[a-z]`)
- Autosave skips file/signature values >50KB to stay under localStorage ~5MB limit
- `populateForm()` calls wrapped in `setTimeout(0)` when called immediately after `buildForm()` to account for list/repeater initial DOM setup timing

---

### 2026-03-04 — Fix Blank-Canvas Detection for Signature Field (#17)
**Issues:** #17 (Add signature field type)

- Fixed required-field validation for signature fields — `canvas.toDataURL()` always returns a non-empty base64 string even for a blank canvas, so validation was passing without any drawing
- Added `isCanvasBlank()` utility in `index.html` that checks the alpha channel of all pixels to determine if the canvas has actual drawn content
- Updated `endDraw()` to set the hidden input to empty string when canvas is blank, making the existing `validateForm()` logic work correctly for required signatures
- No changes needed to `validateForm()`, `collectFormData()`, schemas, CSS, templates, or tests
- All 46 tests pass with no regressions

**Decisions:**
- Used alpha-channel pixel scanning (`getImageData`) rather than comparing `toDataURL()` against a reference blank — more robust across browsers and canvas sizes
- Set hidden input to empty string (rather than adding special validation logic) so the existing `!val || val.trim() === ''` check in `validateForm()` handles it naturally

---

### 2026-03-03 — Add Demo Schema Exercising All Field Types, Wizard, and Conditionals
**Issues:** #19

- Created `schemas/field-type-demo.json` — "Event Registration" wizard form with 4 steps, all 17 field types, and 3 `visible_when` conditionals
- Created `templates/field-type-demo.py` — template handling all field types including JSON-parsed address, repeater, file, and signature
- Created `tests/fixtures/field-type-demo_sample.json` — comprehensive sample data
- Added 2 template tests (`test_field_type_demo_generates_valid_docx`, `test_field_type_demo_with_empty_data`)
- All 46 tests pass; schema validates against `_schema.spec.json`

**Conditional visibility demonstrated:**
- `venue_address` (address) → shown when `attendance_mode` = "In-person"
- `dietary_restrictions` (checkbox) → shown when `attendance_mode` = "In-person"
- `virtual_platform` (text) → shown when `attendance_mode` = "Virtual"

---

### 2026-03-03 — Filter _schema.spec.json from Schema Picker
**Issues:** #26

- `_schema.spec.json` was appearing in the web UI schema picker and failing to load when selected
- Added `!f.name.startsWith('_')` filter in `index.html` to exclude all `_`-prefixed JSON files from the listing
- Convention: `_`-prefixed files in `schemas/` are internal infrastructure, not form definitions

---

### 2026-03-03 — Updated FIELD_TYPES.md to Reflect Current Project State
**Issues:** documentation maintenance

- Verified all 17 field types in `schemas/_schema.spec.json` `fieldType` enum match what is documented.
- Added `maxLength` to the `text` type section — the spec allows it on both `text` and `longtext`, but the old doc only mentioned it under `longtext`.
- Corrected `longtext` `maxLength` behavior: defaults to `5000` in the counter display, does not hard-truncate, only turns the counter red when exceeded.
- Clarified `currency` behavior: `step="0.01"` and `min="0"` are fixed in the browser regardless of schema; `currency_symbol` defaults to `"$"`.
- Noted that `hidden` restores `default_value` on form reset (handled in `resetForm()` in `index.html`).
- Added explicit note that `min`/`max`/`step` are forbidden on all types except `number`, and `currency_symbol` is forbidden on all types except `currency`, per the schema spec `allOf` constraints.
- Added "Common Optional Properties" table covering `required`, `placeholder`, `hint`, and `visible_when` as cross-cutting concerns.
- Rewrote `list` section to clarify the bulk-paste converts on blur (not on input), and that one empty row is pre-populated on render.
- Updated `address` section to document the actual sub-input IDs (`{id}_street`, `{id}_city`, `{id}_state`, `{id}_zip`) and note the absence of an `id = field.id` element.
- Updated `repeater` section to explicitly list permitted sub-field types (`text`, `email`, `tel`, `number`, `currency`, `select`) sourced from `repeaterFieldType` in the spec; noted `min_rows` behavior (remove button disabled at minimum).
- Added a dedicated "Conditional Visibility (`visible_when`)" section documenting: schema shape, CSS class mechanics, validation skip behavior, supported source types per listener attachment logic in `setupConditionalVisibility()`, and target type limitations (types without a direct `id = field.id` element — `checkbox`, `radio`, `list`, `address`, `repeater`, `heading` — do not work reliably as targets).
- Added note that `heading` cannot be used as a `visible_when` target (no `id = field.id` element rendered).

### 2026-03-03 — Updated TEMPLATE_GUIDE.md to Reflect Current Project State
**Issues:** documentation maintenance

- Rewrote `docs/TEMPLATE_GUIDE.md` to accurately reflect the `_base` module introduced in issue #3 and all field types added in issue #2
- Added a dedicated `_base` Module section documenting all six helpers (`new_doc`, `add_table_section`, `add_longtext`, `add_bullet_list`, `add_signatures`, `finalize`) with signatures, parameter descriptions, and usage examples drawn from the actual source in `templates/_base.py`
- Added the full color palette table (`COLOR_DARK_NAVY`, `COLOR_MEDIUM_BLUE`, `COLOR_SOFT_BLUE`, `COLOR_MUTED`, `COLOR_LIGHT_MUTED`) with hex values and intended usage
- Expanded the data dictionary table to cover all 17 field types including `number`, `currency`, `hidden`, `address`, `file`, `signature`, `repeater`; clarified that `heading` is never present in `data`
- Added a Conditional Fields section explaining that `visible_when`-hidden fields arrive as empty strings and require no special template handling — normal empty-check guards suffice
- Added a Wizard Forms section explaining that wizard mode is UI-only; `generate_docx(data)` receives the same flat dict regardless of whether a schema uses `"wizard": true`
- Added Parsing Complex Field Types section with code snippets for `address` (JSON object parse), `repeater` (JSON array parse and iteration), `file`/`signature` (base64 decode and `doc.add_picture()`), `number`/`currency` (numeric conversion with `try/except`), `checkbox` (split on comma), `longtext`/`list` (split on newline)
- All parse examples include `try/except` guards matching the pattern used in `templates/expense-report.py`
- Updated local testing instructions to reference `PYTHONPATH=. python -m pytest tests/ -v` and the `tests/fixtures/` directory; replaced the outdated one-liner with the `importlib.util.spec_from_file_location()` pattern used by the actual test suite
- Removed the Helper Function Pattern section (superseded by the `_base` module documentation)
- Removed hand-rolled signature block, key-value table, and `add_bullet_list` snippets that duplicated `_base` internals; retained only the Manual key-value table and colored footer examples under Common python-docx Patterns for cases requiring direct `python-docx` control

---

### 2026-03-03 — Updated SCHEMA_GUIDE.md to Reflect Current Project State
**Issues:** documentation maintenance

- Added `wizard` to the top-level structure table with type, required, and description columns
- Added `step` to the sections table (optional integer, minimum 1, defaults to index + 1)
- Expanded the field properties table to cover all spec-enforced properties: `default_value`, `fields`, `maxLength` (text + longtext), `min`/`max`/`step` (number only), `currency_symbol` (currency only), `accept`/`max_size_mb` (file only), `min_rows`/`max_rows` (repeater only), `visible_when`
- Corrected `maxLength` documentation: allowed on both `text` and `longtext` (was listed as `longtext` only in the old field table)
- Added field types table listing all 17 types with their `options` requirement and special properties
- Added "Wizard Mode" section with schema example, explanation of `step` defaulting, per-step validation behavior, and non-wizard backward compatibility note
- Added "Conditional Visibility" section with full `visible_when` schema example, property table, and behavior details (hidden fields skip required validation, always collected as empty string, source can appear anywhere, multiple dependents supported)
- Added "Repeater Sub-Fields" section with sub-field type restriction list and template note
- Added "Validation" section with local validation command
- Updated top-level and section tables to include `Type` column and `additionalProperties: false` note
- Updated field ID documentation with explicit pattern explanation and failure examples (uppercase, hyphen, leading digit)
- Added a note to the file location section that `_schema.spec.json` is excluded from the picker

---

### 2026-03-03 — Updated README.md to Reflect Current Project State
**Issues:** documentation maintenance

- Rewrote `README.md` to accurately reflect all features added in issues #2–#9
- Added wizard mode (`"wizard": true`) section with schema example
- Added conditional field visibility (`visible_when`) section with schema example
- Updated the field type table to cover all 17 supported types (was previously showing only 10)
- Updated project structure tree to include `_schema.spec.json`, `_base.py`, individual test files with counts, and all docs
- Updated "Adding a New Form" template example to use `_base` helpers instead of raw `python-docx`
- Added CI section describing the GitHub Actions workflow (`validate.yml`) and the 44-test count
- Removed outdated manual template testing snippet (still available in `docs/TEMPLATE_GUIDE.md`)

---

### 2026-03-03 — CI with GitHub Actions (#9)
**Issues:** #9 (Set up CI with GitHub Actions)

- Created `.github/workflows/validate.yml` with two jobs: schema validation and pytest
- Triggers on `push` and `pull_request` to `develop` and `main` branches
- Uses `ubuntu-latest`, Python 3.12, installs `python-docx`, `jsonschema`, `pytest`
- Schema validation step validates all `schemas/*.json` (excluding `_schema.spec.json`) against the spec
- Test step runs `PYTHONPATH=. pytest tests/ -v` (44 tests)

**Decisions:**
- Scoped triggers to `develop` and `main` branches only — avoids unnecessary CI runs on ephemeral branches
- Used inline Python for schema validation rather than a separate script — keeps the repo simple and avoids adding a new file for a few lines of code
- Followed the workflow structure from `docs/FORMFORGE_EXPANSION_GUIDE.md` Section 8

---

### 2026-03-03 — Conditional Field Visibility with `visible_when` (#7)
**Issues:** #7 (Add conditional/dynamic field visibility)

- Updated `schemas/_schema.spec.json` to allow optional `visible_when` object on field definitions with required `field` (matching field ID pattern) and `equals` (string) properties, plus `additionalProperties: false`
- Added `setupConditionalVisibility()` in `index.html` — builds a dependency map from source field IDs to dependent fields, attaches `change`/`input` event listeners based on source field type (select/radio use `change`, text/textarea use `input`+`change`), and evaluates initial state
- Added `getFieldValue()` helper that handles radio, checkbox, and standard input/select value retrieval
- Added `isFieldConditionallyHidden()` check used by `validateForm()` and `wizardValidateStep()` to skip validation of hidden conditional fields
- `collectFormData()` unchanged — always collects all fields (hidden ones return empty strings), ensuring templates always receive every key
- `resetForm()` calls `setupConditionalVisibility()` after reset to re-evaluate all conditions
- Added CSS class `conditional-hidden` with `display: none`
- Added 5 new tests to `tests/test_schemas.py`: visible_when validates, missing field rejected, missing equals rejected, extra property rejected, existing schemas regression
- All 44 tests pass

**Decisions:**
- `visible_when` uses simple `equals` string matching — sufficient for the current use case and keeps the schema spec clean. More complex operators (not_equals, contains, etc.) can be added later by extending the `visible_when` object
- Conditional fields are hidden via a CSS class on `.field-group` rather than removing from DOM — preserves form state so Back button in wizard mode doesn't lose data
- `collectFormData()` always includes hidden conditional fields (as empty strings) rather than omitting them — ensures templates always receive a consistent set of keys regardless of visibility state
- Event listeners support order-independent references: a field can depend on a source that appears later in the schema since listeners are attached after all fields are rendered
- Multiple fields can depend on the same source field via the dependency map pattern

---

### 2026-03-03 — Multi-Step Wizard Form Support (#6)
**Issues:** #6 (Add multi-step wizard form support)

- Updated `schemas/_schema.spec.json` to allow optional `"wizard": true` boolean at the top level and optional `"step"` (positive integer, minimum 1) on section objects
- Added wizard CSS styles to `index.html`: step indicator with circles, connectors, and labels; navigation buttons; section visibility toggling
- Modified `buildForm()` in `index.html` to detect `wizard: true` and render a step indicator, show only one section at a time, and add Next/Back navigation buttons per section
- Added `wizardValidateStep()` for per-step validation — clicking Next validates only the current section's required fields before advancing
- Added `wizardNext()` and `wizardGoTo()` for step navigation with indicator state updates (active/completed styling)
- Back button hidden on first step; submit area hidden until last step; data preserved across step navigation
- Non-wizard schemas render exactly as before — no visual or behavioral changes
- Added 6 new tests to `tests/test_schemas.py`: wizard schema validation, wizard without step, non-wizard regression, rejects non-boolean wizard, rejects non-integer step, rejects step zero
- All 39 tests pass

**Decisions:**
- Wizard navigation buttons are placed inside each section div rather than in a fixed footer — keeps the flow natural and avoids layout conflicts with the existing submit area
- Submit area (`Export to DOCX` + `Reset`) is hidden during wizard navigation and only shown on the final step, where it replaces the Next button
- Per-step validation reuses the same pattern as `validateForm()` but scoped to one section — `collectFormData()` and full `validateForm()` still operate across all sections for final export
- Step indicator uses numbered circles with connectors — completed steps get accent-glow background, active step gets solid accent fill
- If sections omit `step`, the indicator defaults to section index + 1

---

### 2026-03-03 — Template Testing with pytest (#5)
**Issues:** #5 (Set up template testing with pytest)

- All test infrastructure was created during issues #3 and #4:
  - `tests/test_schemas.py` (15 tests): validates all schemas against `_schema.spec.json`, plus 9 negative tests for invalid schemas
  - `tests/test_templates.py` (4 tests): runs `generate_docx()` for onboarding and expense-report with sample and empty data, verifies valid DOCX output (bytes, non-empty, PK magic bytes)
  - `tests/test_base.py` (14 tests): unit tests for all `_base.py` utilities
  - `tests/fixtures/onboarding_sample.json` and `expense-report_sample.json` with field IDs matching their schemas
- Templates loaded via `importlib.util.spec_from_file_location()` with `sys.path` including `templates/` so `import _base` resolves
- All 33 tests pass with `PYTHONPATH=. python -m pytest tests/ -v`
- No external services or network access required — fully offline

**Decisions:**
- Issue #5 was fully satisfied by work in #3 and #4 — no additional code needed, just verified and closed

---

### 2026-03-03 — Added Schema Validation with `_schema.spec.json` (#4)
**Issues:** #4 (Add schema validation)

- Created `schemas/_schema.spec.json` using JSON Schema draft 2020-12 to validate all form schemas
- Spec validates top-level structure (`title`, `sections`), section structure (`title`, `fields`), and field structure (`id` pattern, `label`, `type` enum)
- All 17 field types enumerated in the `type` enum with type-specific conditional validation via `if/then/allOf`
- Conditional rules enforce: `options` required for select/radio/checkbox, `default_value` for hidden, `fields` for repeater
- Type-specific properties restricted to their correct types (e.g., `min/max/step` only on `number`, `maxLength` only on `text/longtext`, `accept/max_size_mb` only on `file`)
- Repeater sub-fields validated separately with restricted type enum (`text`, `email`, `tel`, `number`, `currency`, `select`)
- Created `tests/test_schemas.py` with 15 tests: spec validity, field type coverage, positive validation of both existing schemas, and 9 negative tests for invalid schemas
- Both `onboarding.json` and `expense-report.json` validate successfully against the spec

**Decisions:**
- Used `if/then` within `allOf` for conditional validation rather than `oneOf` with separate schemas per type — keeps the spec more readable and maintainable
- Used `additionalProperties: false` at all levels to catch typos and unknown properties early
- Template path pattern enforced as `^templates/.+\.py$` to match the project convention
- Repeater sub-fields defined as a separate `$defs/repeaterField` schema with its own restricted type enum, matching the subset supported by the app

---

### 2026-03-03 — Created Shared Template Base `_base.py` (#3)
**Issues:** #3 (Create shared template base)

- Created `templates/_base.py` with 6 shared utilities: `new_doc()`, `add_table_section()`, `add_longtext()`, `add_bullet_list()`, `add_signatures()`, `finalize()`
- Exported a standard color palette (`COLOR_DARK_NAVY`, `COLOR_MEDIUM_BLUE`, `COLOR_SOFT_BLUE`, `COLOR_MUTED`, `COLOR_LIGHT_MUTED`)
- Refactored `templates/onboarding.py` to use `_base` helpers — removed ~90 lines of duplicated helper functions
- Refactored `templates/expense-report.py` to use `_base` helpers for shared patterns (table sections, colors, finalize)
- Updated `index.html` with `loadBaseModule()` function that fetches `_base.py` and writes it to Pyodide's virtual filesystem via `pyodide.FS.writeFile()`, enabling standard `import _base` in templates
- `loadBaseModule()` is called once before any template execution; `baseModuleLoaded` flag prevents re-fetching
- Added `baseModuleLoaded` reset on repo change so new repos get their own `_base.py`
- Created `tests/test_base.py` (14 tests) covering all 6 utilities, color constants, and edge cases
- Created `tests/test_templates.py` (4 tests) verifying both templates produce valid DOCX with sample and empty data
- Created `tests/fixtures/onboarding_sample.json` sample fixture

**Decisions:**
- Used Pyodide's `FS.writeFile()` to place `_base.py` on the virtual filesystem rather than `exec()` into globals — this allows templates to use standard `import _base` syntax that works identically in regular Python and Pyodide
- Kept `Calibri` as the default font (matching existing templates) rather than `Segoe UI` from the expansion guide sketch
- Added optional `font_name` and `font_size` parameters to `new_doc()` for template customization while maintaining backward compatibility
- `loadBaseModule()` tries the connected GitHub repo first, falls back to the FormForge repo on GitHub — works for both custom repos and the demo/local file paths
- Expense report template retains its own signature handling (base64 image embedding) rather than using `add_signatures()` since it needs specialized canvas-to-image logic

---

### 2026-03-03 — Implemented All 8 New Field Types (#2)
**Issues:** #2, #11 (number), #12 (currency), #13 (heading), #14 (hidden), #15 (address), #16 (file), #17 (signature), #18 (repeater), #19 (demo schema)

- Added 8 new field types to `createField()`, `collectFormData()`, `validateForm()`, and `resetForm()` in `index.html`
- Added CSS styles for all new field types (currency wrapper, heading divider, address group, file upload with preview, signature canvas pad, repeater rows)
- Updated `buildForm()` layout: `number` and `currency` pair in 2-column rows; `hidden` skipped from visible layout
- Created `schemas/expense-report.json` — demo form exercising all 8 new types plus existing types
- Created `templates/expense-report.py` — handles JSON parsing for address/repeater, base64 decoding for file/signature, currency formatting
- Created `tests/fixtures/expense-report_sample.json` — sample data for template testing
- Updated `docs/FIELD_TYPES.md` with all 8 new types: JSON schema examples, schema properties, and template handling code

**Decisions:**
- Heading fields return early from `createField()` to skip the default hint rendering (they handle their own hint)
- Hidden fields use `default_value` schema property; the field group is `display: none`
- Address data is serialized as a JSON object string; validation checks street is non-empty when required
- Signature uses `canvas.toDataURL('image/png')` saved to a hidden input on each `mouseup`/`touchend`
- Repeater stores sub-field config via `wrapper.dataset.subFields` for `collectFormData()` to reference
- Repeater sub-fields support text, email, tel, number, currency, and select types
- File upload validates size client-side via `max_size_mb` and shows image preview for image types

---

### 2026-03-03 — Implementation Plan for #2 (New Field Types)
**Issues:** #2, #11–#19

- Analyzed existing codebase: `createField()` (L1393–1541), `collectFormData()` (L1604–1624), form layout (L1341–1391)
- Broke #2 into 9 sub-issues organized by complexity tier:
  - **Tier 1 (simple):** #11 number, #12 currency, #13 heading, #14 hidden
  - **Tier 2 (complex):** #15 address, #16 file, #17 signature, #18 repeater
  - **Integration:** #19 demo schema exercising all new types
- Each issue includes: schema properties, implementation touchpoints, CSS needs, template handling, and acceptance criteria

**Decisions:**
- Implementation order follows the priority in issue #2: number/currency first, heading/hidden next, then complex types
- Repeater depends on Tier 1 types being complete (sub-fields may use number, currency, etc.)
- Data formats: address → JSON object string, repeater → JSON array string, signature/file → base64 string
- Hidden fields use `default_value` schema property (not `value`, to avoid confusion with HTML attribute)
- Heading fields skip `collectFormData()` and `validateForm()` entirely
- Currency defaults to `$` symbol with `step="0.01"`

---

### 2026-03-03 — Project Initialization Complete
**Issues:** #1 (Project Initialization)

- Added `README.md` with project overview, architecture, field types, usage instructions, and how to add forms
- Added `LICENSE` (MIT)
- Created `tests/` and `tests/fixtures/` directories
- Created `.github/workflows/` directory (ready for CI in issue #9)
- Added `.gitignore` for Python, Node, OS, and IDE files
- Verified `schemas/` and `templates/` directories already in place

**Decisions:**
- Chose MIT license for maximum permissiveness
- Used `.gitkeep` files to track empty directories in git

---

### 2026-03-03 — Project Setup
**Issues:** #1 (Project Initialization)

- Created GitHub repo `ccirone2/form-forge` with default branch `develop`
- Added initial `schemas/` and `templates/` directories
- Added `docs/FORMFORGE_EXPANSION_GUIDE.md` as the project roadmap
- Created GitHub issues #1–#9 covering all expansion areas from the guide
- Created this DEVLOG to track progress going forward

**Decisions:**
- Using `develop` as the default branch; `main` reserved for stable releases
- Staying client-side only — no server, no database, no auth (beyond GitHub)
- GitHub serves as the CMS for schemas and templates
