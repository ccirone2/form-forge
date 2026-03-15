# FormForge — Feature Plans

> Structured implementation plans for upcoming features.
> Branches are created from `develop`. Issues are linked to each task.

---

TODO: Schema context menu improvements — add option to add base scaffold (e.g. editor is blank)

---

## Completed Plans

### Issue #172 — Unified Autofill Dropdown ✅

**Branch:** `feature/172-unified-autofill`
**Issues:** #172, #173, #174, #175, #176

Consolidated Profiles, Presets, and data-loading actions into a single `[Autofill ▾]` button. Added explicit `_profileName` to profiles. Bottom toolbar simplified to `[Save Data]` `[Reset]`.

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
