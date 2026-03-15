# FormForge — Feature Plans

> Structured implementation plans for upcoming features.
> Branches are created from `develop`. Issues are linked to each task.

---

### Unified Autofill Dropdown — Consolidate Presets, Profiles & Data Loading

**Branch:** `feature/172-unified-autofill`
**Implementation order:** Named Profiles → Unified Dropdown UI → Migrate Data Actions → Tests & Cleanup

#### Problem

Three closely related features (profiles, presets, load sample/paste/file data) are spread across two separate UI locations with inconsistent patterns:
- **Top toolbar:** `[Profiles]` `[Presets]` — two separate buttons with separate dropdowns
- **Bottom toolbar:** `[Save Data]` `[Load Data]` `[Paste Data]` `[Load Sample]` `[Reset]`

All of these do the same conceptual thing: populate form fields with data. The scattered layout increases cognitive load and button clutter.

Additionally, profiles auto-derive their display name from field values rather than letting users name them explicitly (unlike presets, which are user-named).

#### Design

Single `[Autofill ▾]` button replaces both `[Profiles]` and `[Presets]` in the top form nav. The dropdown has three sections:

```
┌──────────────────────────────────────┐
│ PROFILES                         [+] │
│  Jane Doe · jane@acme.com        ⋮   │
│  Bob Smith · bob@co.org          ⋮   │
├──────────────────────────────────────┤
│ PRESETS                          [+] │
│  Standard Weekly · 5 fields      ⋮   │
│  New Hire Default · 8 fields     ⋮   │
├──────────────────────────────────────┤
│ ▸ Load Sample Data                   │
│ ▸ Paste Data…                        │
│ ▸ Load from File…                    │
└──────────────────────────────────────┘
```

- **Profiles section:** Shows saved profiles with name + preview. `[+]` opens profile editor. Profiles now have an explicit `name` field (user-editable), with auto-detected name as placeholder/default.
- **Presets section:** Shows schema-specific presets with name + field count. `[+]` opens preset editor. Unchanged data model.
- **Actions section:** Quick-access items that open existing modals/pickers (Paste Data modal, file picker, sample data fetch). These move up from the bottom toolbar.
- **Bottom toolbar simplifies to:** `[Export to DOCX]` | `[Save Data]` `[Reset]`

#### Tasks

| # | Task | Dependencies | Files |
|---|------|-------------|-------|
| 1 | Add `name` field to profile data model and editor | — | `index.html` |
| 2 | Build unified Autofill dropdown component | Task 1 | `index.html` |
| 3 | Migrate Load Sample, Paste Data, Load File into dropdown actions | Task 2 | `index.html` |
| 4 | Clean up bottom toolbar and remove old Profiles/Presets buttons | Task 3 | `index.html` |
| 5 | Update tests for new UI structure | Task 4 | `tests/test_dev_mode.py` |
| 6 | Update DEVLOG and documentation | Task 5 | `docs/DEVLOG.md` |

#### Implementation Notes

- Profile `name` field: Add to profile editor as first field. Migration: existing profiles without `name` get auto-detected name written as `name` on first load.
- Unified dropdown reuses existing `showPresetDropdown` / `showProfileDropdown` rendering logic but composes them into a single container.
- Field-level profile indicators (the person icon on focused fields) remain unchanged — they open a filtered view of the profiles section only.
- The Paste Data modal remains a separate modal (not inline in dropdown) — the dropdown action item just opens it.
- Badge on `[Autofill ▾]` shows combined count of profiles + presets when > 0.

---

TODO: Schema context menu improvements — add option to add base scaffold (e.g. editor is blank)

---

## Completed Plans

### Issues #161, #162, #163 — Paste Data, Presets, Bundle Export/Import ✅

**Plan:** `~/.claude/plans/cuddly-churning-tower.md`
**Implementation order:** Paste Data → Presets → Bundle

| # | Feature | Branch | Sub-issues | Status |
|---|---------|--------|------------|--------|
| #161 | Clipboard Paste for Form Data | `feature/161-paste-data` | — | Done |
| #162 | Per-Schema Presets | `feature/162-per-schema-presets` | #164, #165, #166 | Done |
| #163 | Bundle Export/Import | `feature/163-bundle-export-import` | #167, #168 | Done |

### Issue #143 — Unified Content Source & Tab-Based Navigation ✅

**Branch:** `feature/143-unified-tabs`
**Issues:** #143, #144, #145, #146, #147, #148, #149, #150

Eliminated Dev Mode toggle and replaced with always-visible 4-tab navigation (Forms | Schema | Template | Docs). Merged dual GitHub connection state into single content source. Promoted local folder to first-class source on Forms tab. Added bidirectional form/editor flow with edit actions on picker cards and fill actions in schema preview.

### Issue #40 — Improve Test Coverage ✅

**PR:** #82 (merged)

Upgraded test suite from smoke-only checks to meaningful content verification, added missing coverage paths, and modernized test patterns.
