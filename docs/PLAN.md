# FormForge — Feature Plans

> Structured implementation plans for upcoming features.
> Branches are created from `develop`. Issues are linked to each task.

---

TODO: Schema context menu improvements — add option to add base scaffold (e.g. editor is blank)

---

## Active Plans

*(No active plans.)*

---

## Completed Plans

### Issue #202 — Commit New Files from Editors to GitHub ✅

**Branch:** `feature/202-commit-new-files`
**Issue:** #202

Added `devGhRegisterNewFile()` to register editor content as new workspace files, updated save/commit/toolbar flows to support creating files in GitHub repos (including empty repos), with post-commit picker refresh.

### Issues #192–#196 — UI/UX Audit Fixes ✅

**Branch:** `feature/192-ui-ux-audit`
**Issues:** #192, #193, #194, #195, #196
**Plan:** `~/.claude/plans/ui-ux-audit-192.md`

Fixed 55 UI/UX audit findings across 4 priority tiers: P0 critical a11y gaps, P1 design token normalization + modal a11y, P2 editor performance + responsive design, P3 design system refinements.

### Issue #198 — Embed Full Documentation in Docs Tab ✅

**Branch:** `feature/198-embed-docs`
**Issues:** #198
**Plan:** `~/.claude/plans/breezy-hatching-sprout.md`

Embedded full markdown docs in `index.html` as JS constants with sync script and CI check. Removed GitHub fetch path and abbreviated fallback functions.

### Issue #190 — Eliminate ghToolbar ✅

**Branch:** `feature/190-eliminate-ghtoolbar`
**Issues:** #190
**PR:** #191

Removed the global `#ghToolbar` bar and merged its branch controls (branch select, create-branch, refresh) into the per-editor source toolbars for both Schema and Template tabs.

### Issues #185, #186–#189 — Forms Tab UX Improvements ✅

**Issues:** #185
**PRs:** #186, #187, #188, #189

UX improvements: demo→open button swap, disconnect moved to connect dialog, inline "Open Form" button on picker cards, clean Forms tab layout when connected.

### Issues #181, #182, #183 — Button Icon, Source Persistence, Docs Refresh ✅

**PR:** #184

Three bug fixes: missing `icon-link` SVG symbol (#181), GitHub connection persistence to localStorage (#182), docs tab fetching from connected repo (#183).

### Issue #159 — Info Field Type & Repeater Table Display ✅

**Branch:** `feature/159-info-repeater-table`
**Issues:** #159
**PR:** #160

Added new `info` field type (read-only display block with info/warning/success styles) and `display: "table"` mode for repeater fields.

### Issue #157 — Git Controls in Editor Tabs ✅

**Branch:** `feature/157-git-controls`
**Issues:** #157
**PR:** #158

Restored git operations (branch select, new branch, refresh, disconnect, commit/push) that became unreachable when the workspace view was removed in PR #151.

### Issue #172 — Unified Autofill Dropdown ✅

**Branch:** `feature/172-unified-autofill`
**Issues:** #172, #173, #174, #175, #176

Consolidated Profiles, Presets, and data-loading actions into a single `[Autofill ▾]` button. Added explicit `_profileName` to profiles. Bottom toolbar simplified to `[Save Data]` `[Reset]`.

### Issues #161, #162, #163 — Paste Data, Presets, Bundle Export/Import ✅

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
