# FormForge — Feature Plans

> Structured implementation plans for upcoming features.
> Branches are created from `develop`. Issues are linked to each task.

---

## Active Plans

*(No active plans.)*

---

## Completed Plans

### Issue #233 — Fix Signature Canvas Drawing Offset ✅

**Branch:** `feature/233-signature-offset`
**Issue:** #233
**PR:** #234

Fixed double-DPR scaling in `getPos()` within `createSignatureField()` that caused signature strokes to draw offset from the cursor on high-DPI displays.

### Issue #230 — Stencil Fluent Builder Class ✅

**Branch:** `feature/230-stamp-class`
**Issue:** #230
**PRs:** #231, #232

Added `Stencil` fluent builder class (originally named `Stamp`, renamed in PR #232) to `stencils.py` for method-chaining document construction. Updated all templates to use the new class. Existing module-level functions retained for backward compatibility.

### Issue #227 — Optional new_doc() Title ✅

**Branch:** `feature/227-optional-new-doc-title`
**Issue:** #227
**PR:** #228

Made `title_text` parameter optional in `new_doc()` (default `""`), allowing `new_doc()` to be called with no arguments for coverpage-based templates.

### Issue #226 — SVG Support & Coverpage Layout ✅

**Branch:** `feature/226-svg-support-coverpage-layout`
**Issue:** #226
**PR:** #229

Added client-side SVG-to-PNG rasterization in `createFileField()`, `max_logo_height` and `max_height` params to `coverpage()` and `image()`, and adaptive spacer in `coverpage()` to prevent page overflow.

### Issue #223 — Auto-Preview & DOCX Rendering Fidelity ✅

**Branch:** `feature/223-auto-preview-fidelity`
**Issue:** #223
**PR:** #224

Auto-runs template preview on first Template tab visit when template and sample data are present. Added mammoth.js style mapping and enhanced preview CSS for improved DOCX rendering fidelity.

### Issue #222 — Coverpage Stencil ✅

**Branch:** `feature/222-coverpage-stencil`
**Issue:** #222
**Plan:** `~/.claude/plans/glowing-honking-sloth.md`

Added `coverpage()` stencil function for professional document cover pages: company logo with geometric bar, title/type at ~2/3 page, configurable metadata fields, page break. Includes demo schema+template, 8 tests, and docs updates.

### Issue #215 — Improve Editor Context Menus ✅

**Branch:** `feature/215-context-menu-improvements`
**Issues:** #215 (parent), #216, #217, #218, #219

Redesigned Schema and Template editor context menus: cursor-aware (root/section/field and top/body contexts), flat (group labels, no submenus), editor-clamped (bounding element positioning), with field property snippets and base scaffold option.

### Issue #214 — Demo Editor Loading ✅

**Branch:** `feature/214-demo-editor-loading`
**Issue:** #214
**PR:** #220

Auto-loads `DEMO_SCHEMA` and `DEMO_TEMPLATE` into Schema and Template editors when in demo mode. Added "Reset to Demo" toolbar control for restoring original demo content after edits.

### Issue #212 — Tokenize Sidebar CSS ✅

**Branch:** `feature/212-tokenize-sidebar-css`
**Issue:** #212
**PR:** #213

Replaced ~20 hard-coded pixel values in sidebar CSS with new design tokens (`--space-*`, `--sidebar-width`, `--sidebar-collapsed-width`, `--border-width-accent`, `--icon-sm`) in `:root`.

### Issues #208, #209 — Sidebar Navigation & Contextual Help ✅

**Branches:** `feature/208-sidebar-navigation`, `feature/209-sidebar-navigation`
**Issues:** #208, #209
**PRs:** #210 (closed, superseded), #211 (merged)

Converted horizontal top navigation to a persistent left sidebar layout with collapse/expand, mobile bottom nav, and localStorage persistence (#208). Added contextual help sidebars to Schema and Template editors with field type reference, stencils API reference, search/filter, and insert-on-click (#209).

### Issue #205 — LLM Context Export ✅

**Branch:** `feature/205-llm-context-export`
**Issue:** #205
**PR:** #206

Added per-guide Copy and Download buttons in Docs tab. Added "Copy AI Context" buttons to Schema and Template editor toolbars that assemble LLM-optimized context bundles.

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
