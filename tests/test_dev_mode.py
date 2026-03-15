"""Tests for developer tooling in index.html.

Since the developer tools are client-side JavaScript, these tests validate:
1. HTML structure: required elements, CDN dependencies, SVG symbols
2. Schema Builder: starter schema validates against spec
3. Field snippets: all snippet types are valid against the spec
4. Template Builder: starter template is valid Python with generate_docx
5. CSS: all referenced CSS classes exist in the stylesheet
"""

import json
import re
from pathlib import Path

import jsonschema
import pytest

# --- CDN Dependencies ---


def test_prism_css_loaded(index_html: str) -> None:
    assert "prismjs@1.29.0/themes/prism-tomorrow.min.css" in index_html


def test_prism_js_loaded(index_html: str) -> None:
    assert "prismjs@1.29.0/prism.min.js" in index_html


def test_prism_json_language_loaded(index_html: str) -> None:
    assert "prism-json.min.js" in index_html


def test_prism_python_language_loaded(index_html: str) -> None:
    assert "prism-python.min.js" in index_html


def test_codejar_loaded(index_html: str) -> None:
    assert "codejar@4.2.0" in index_html


def test_mammoth_loaded(index_html: str) -> None:
    assert "mammoth@1.6.0" in index_html


# --- SVG Symbols ---


def test_icon_wrench_exists(index_html: str) -> None:
    assert 'id="icon-wrench"' in index_html


def test_icon_refresh_exists(index_html: str) -> None:
    assert 'id="icon-refresh"' in index_html


def test_icon_folder_open_exists(index_html: str) -> None:
    assert 'id="icon-folder-open"' in index_html


# --- HTML Structure ---


def test_dev_nav_exists(index_html: str) -> None:
    assert 'id="mainNav"' in index_html
    assert 'class="dev-nav-tab' in index_html


def test_dev_nav_has_four_tabs(index_html: str) -> None:
    assert index_html.count('class="dev-nav-tab') == 4


def test_view_dev_schema_exists(index_html: str) -> None:
    assert 'id="view-dev-schema"' in index_html


def test_view_dev_template_exists(index_html: str) -> None:
    assert 'id="view-dev-template"' in index_html


def test_context_menu_exists(index_html: str) -> None:
    assert 'id="ctxMenu"' in index_html


def test_schema_editor_exists(index_html: str) -> None:
    assert 'id="schemaEditor"' in index_html


def test_template_editor_exists(index_html: str) -> None:
    assert 'id="templateEditor"' in index_html


def test_sample_data_editor_exists(index_html: str) -> None:
    assert 'id="sampleDataEditor"' in index_html


def test_schema_preview_form_exists(index_html: str) -> None:
    assert 'id="schemaPreviewForm"' in index_html


def test_docx_preview_container_exists(index_html: str) -> None:
    assert 'id="docxPreviewContainer"' in index_html


def test_no_orphaned_workspace_view(index_html: str) -> None:
    """Workspace view was removed — no view-dev-workspace element should exist."""
    assert 'id="view-dev-workspace"' not in index_html


def test_forms_tab_exists(index_html: str) -> None:
    """Nav should have a Forms tab with data-tab attribute."""
    assert 'data-tab="forms"' in index_html


def test_no_dev_mode_toggle(index_html: str) -> None:
    """toggleDevMode function should not exist in the refactored app."""
    assert "function toggleDevMode" not in index_html


def test_no_dev_mode_variable(index_html: str) -> None:
    """let devMode variable should not exist in the refactored app."""
    assert "let devMode" not in index_html


def test_source_grid_exists(index_html: str) -> None:
    """Source grid CSS class should be defined."""
    assert ".source-grid" in index_html


def test_connect_local_folder_exists(index_html: str) -> None:
    """connectLocalFolder function should exist."""
    assert "function connectLocalFolder" in index_html


def test_edit_schema_btn_exists(index_html: str) -> None:
    """Edit schema button should exist in form nav."""
    assert 'id="editSchemaBtn"' in index_html


def test_fill_form_from_editor_exists(index_html: str) -> None:
    """fillFormFromEditor function should exist."""
    assert "function fillFormFromEditor" in index_html


def test_no_default_repo_value(index_html: str) -> None:
    """repoInput should not have a default value attribute with a repo path."""
    match = re.search(r'id="repoInput"[^>]*>', index_html)
    assert match
    tag = match.group(0)
    assert 'value="ccirone2/form-forge"' not in tag


# --- CSS Sections ---


def test_css_section_31_dev_mode_core(index_html: str) -> None:
    assert "31. DEV MODE CORE" in index_html


def test_css_section_32_split_pane(index_html: str) -> None:
    assert "32. DEV SPLIT PANE" in index_html


def test_css_section_33_context_menu(index_html: str) -> None:
    assert "33. CONTEXT MENU" in index_html


def test_css_section_34_template_builder(index_html: str) -> None:
    assert "34. TEMPLATE BUILDER" in index_html


def test_css_section_36_reduced_motion(index_html: str) -> None:
    assert "36. REDUCED MOTION" in index_html


def test_css_section_37_mobile_gate(index_html: str) -> None:
    assert "37. DEV MODE MOBILE GATE" in index_html


def test_mobile_gate_hides_toggle(index_html: str) -> None:
    """The mode toggle must be disabled on narrow viewports."""
    # Find the @media block for 768px in section 36 — toggle is disabled via
    # pointer-events:none (shown but non-interactive) rather than display:none
    pattern = r"@media\s*\(max-width:\s*768px\)\s*\{[^}]*\.mode-toggle\s*\{"
    assert re.search(pattern, index_html), "mode-toggle must be gated at <=768px"


# --- JavaScript Functions ---


_REQUIRED_FUNCTIONS = [
    "showTab",
    "initSchemaEditor",
    "devValidateSchema",
    "devUpdateSchemaPreview",
    "devNewSchema",
    "devLoadSchemaFile",
    "devFormatSchema",
    "devSaveSchema",
    "showContextMenu",
    "hideContextMenu",
    "devSchemaContextItems",
    "devInsertSnippet",
    "devInsertSection",
    "devWrapInWizard",
    "initTemplateEditor",
    "devToggleSampleData",
    "devRunPreview",
    "devNewTemplate",
    "devLoadTemplateFile",
    "devSaveTemplate",
    "initDevResizer",
    "devReadWorkspaceFromHandle",
    "devLoadWorkspaceFile",
    "devSaveToWorkspace",
    "devPollWorkspace",
    "devUpdateLineNumbers",
    "devFindFoldRegions",
    "devToggleFold",
    "devHighlightWithFolding",
    "devGetFoldHiddenLines",
    "devEditorKeydownHandler",
    "devFindTextPosition",
    "devSetCursorOffset",
    "devGetCursorOffset",
    "devGenerateSampleData",
    "devAutoFillSampleData",
    "getFieldAccessor",
    "devCountTemplateFieldRefs",
]


@pytest.mark.parametrize("func_name", _REQUIRED_FUNCTIONS)
def test_js_function_exists(index_html: str, func_name: str) -> None:
    assert f"function {func_name}" in index_html


# --- State Variables ---


_REQUIRED_STATE_VARS = [
    "devSchemaText",
    "devTemplateText",
    "devSampleDataText",
    "devPreviewDebounce",
    "devSchemaValid",
    "schemaJar",
    "templateJar",
    "sampleJar",
    "workspaceHandle",
    "workspaceFiles",
    "devWorkspacePoller",
    "currentWorkspaceFile",
    "devParsedSchema",
]


@pytest.mark.parametrize("var_name", _REQUIRED_STATE_VARS)
def test_state_variable_exists(index_html: str, var_name: str) -> None:
    assert f"let {var_name}" in index_html


# --- Schema Validation: DEV_STARTER_SCHEMA ---


def _extract_js_object(html: str, var_name: str) -> str:
    """Extract a JS object literal assigned to a const."""
    pattern = rf"const {var_name}\s*=\s*(\{{[\s\S]*?\n\}});"
    match = re.search(pattern, html)
    assert match, f"Could not find {var_name} in index.html"
    return match.group(1)


def test_starter_schema_validates_against_spec(index_html: str, spec: dict) -> None:
    """The DEV_STARTER_SCHEMA embedded in JS must be valid per the spec."""
    js_obj = _extract_js_object(index_html, "DEV_STARTER_SCHEMA")
    # Convert JS object to JSON (add quotes to keys)
    json_str = re.sub(r"(\w+)\s*:", r'"\1":', js_obj)
    schema = json.loads(json_str)
    jsonschema.validate(instance=schema, schema=spec)


# --- Field Snippets: all types match the spec ---


def test_field_snippets_cover_all_spec_types(index_html: str, spec: dict) -> None:
    """FIELD_SNIPPETS should have entries for all types in the spec enum."""
    spec_types = set(spec["$defs"]["fieldType"]["enum"])
    # Extract keys from the FIELD_SNIPPETS object
    snippet_block = re.search(
        r"const FIELD_SNIPPETS\s*=\s*\{([\s\S]*?)\n\};", index_html
    )
    assert snippet_block, "FIELD_SNIPPETS not found"
    snippet_keys = set(re.findall(r"^\s*(\w+)\s*:", snippet_block.group(1), re.M))
    assert spec_types == snippet_keys, (
        f"Missing in snippets: {spec_types - snippet_keys}, "
        f"Extra in snippets: {snippet_keys - spec_types}"
    )


# --- Template Builder: starter template ---


def test_starter_template_is_valid_python(index_html: str) -> None:
    """DEV_STARTER_TEMPLATE must be parseable Python."""
    match = re.search(r"const DEV_STARTER_TEMPLATE\s*=\s*`([\s\S]*?)`\s*;", index_html)
    assert match, "DEV_STARTER_TEMPLATE not found"
    template_code = match.group(1)
    compile(template_code, "<dev_starter_template>", "exec")


def test_starter_template_has_generate_docx(index_html: str) -> None:
    """Starter template must define generate_docx."""
    match = re.search(r"const DEV_STARTER_TEMPLATE\s*=\s*`([\s\S]*?)`\s*;", index_html)
    assert match
    assert "def generate_docx(data):" in match.group(1)


def test_starter_template_imports_stencils(index_html: str) -> None:
    """Starter template must import stencils."""
    match = re.search(r"const DEV_STARTER_TEMPLATE\s*=\s*`([\s\S]*?)`\s*;", index_html)
    assert match
    assert "import stencils" in match.group(1)


# --- Security: no raw innerHTML with user content ---


def test_no_unsafe_innerhtml_with_filename(index_html: str) -> None:
    """workspace-file-name must not be set via innerHTML with f.name."""
    assert 'innerHTML = `<span class="workspace-file-name">${f.name}' not in index_html


def test_error_panel_uses_textcontent(index_html: str) -> None:
    """Schema error panel must not use innerHTML for error messages."""
    # Find the devUpdateSchemaPreview function and check error display
    func_match = re.search(
        r"function devUpdateSchemaPreview\(\)([\s\S]*?)^function ",
        index_html,
        re.M,
    )
    assert func_match
    func_body = func_match.group(1)
    # The error display should use textContent, not innerHTML
    assert "errPanel.innerHTML" not in func_body


def test_preview_error_uses_textcontent(index_html: str) -> None:
    """Preview error in devUpdateSchemaPreview uses textContent, not innerHTML."""
    func_match = re.search(
        r"function devUpdateSchemaPreview\(\)([\s\S]*?)^function ",
        index_html,
        re.M,
    )
    assert func_match
    func_body = func_match.group(1)
    assert "errP.textContent" in func_body


def test_devrunpreview_no_string_interpolation_in_python(index_html: str) -> None:
    """devRunPreview must not embed data in Python source via template literals."""
    func_match = re.search(
        r"function devRunPreview\(\)([\s\S]*?)^function ",
        index_html,
        re.M,
    )
    assert func_match
    func_body = func_match.group(1)
    assert "json.loads('''" not in func_body, (
        "Data must not be passed to Python via string interpolation"
    )


# --- Boot sequence ---


def test_no_init_workspace_drop_zone(index_html: str) -> None:
    """initWorkspaceDropZone was removed with workspace view."""
    assert "initWorkspaceDropZone()" not in index_html


# --- Tab whitelist ---


def test_valid_dev_tabs_whitelist(index_html: str) -> None:
    """VALID_TABS must contain all tab names."""
    assert "VALID_TABS" in index_html
    assert "'forms'" in index_html
    assert "'dev-schema'" in index_html
    assert "'dev-template'" in index_html
    assert "'dev-docs'" in index_html


# --- buildForm backward compatibility ---


def test_buildform_has_targetform_param(index_html: str) -> None:
    """buildForm must accept an optional targetForm parameter."""
    assert "function buildForm(schema, targetForm)" in index_html


def test_buildform_conditionally_updates_title(index_html: str) -> None:
    """When targetForm is provided, formTitle should not be updated."""
    # Find the buildForm function
    match = re.search(
        r"function buildForm\(schema, targetForm\)([\s\S]*?)^function ",
        index_html,
        re.M,
    )
    assert match
    body = match.group(1)
    assert "if (!targetForm)" in body
    assert "targetForm || document.getElementById('dynamicForm')" in body


# --- Polling lifecycle ---


def test_polling_stops_after_repeated_errors(index_html: str) -> None:
    """devPollWorkspace must stop after 5 consecutive errors."""
    match = re.search(
        r"function devPollWorkspace\(\)([\s\S]*?)^function ", index_html, re.M
    )
    assert match
    body = match.group(1)
    assert "devPollErrorCount" in body
    assert "clearInterval(devWorkspacePoller)" in body


# ============================================================
#  Tab navigation
# ============================================================


def _extract_func(html: str, name: str) -> str:
    """Extract JS function body from index.html."""
    match = re.search(rf"function {name}\b[^{{]*\{{([\s\S]*?)^function ", html, re.M)
    assert match, f"Function {name} not found"
    return match.group(1)


def test_showtab_persists_tab(index_html: str) -> None:
    """showTab writes active tab to localStorage."""
    body = _extract_func(index_html, "showTab")
    assert "localStorage.setItem('formforge-active-tab'" in body


def test_boot_restores_active_tab(index_html: str) -> None:
    """Boot sequence restores last active tab."""
    assert "formforge-active-tab" in index_html
    # The boot block should read the tab from localStorage
    assert "localStorage.getItem('formforge-active-tab')" in index_html


# ============================================================
#  ISSUE #117 — Schema Builder with live form preview
# ============================================================


def test_schema_editor_debounce_300ms(index_html: str) -> None:
    """Schema editor uses 300ms debounce for preview updates."""
    body = _extract_func(index_html, "initSchemaEditor")
    assert "300" in body
    assert "devPreviewDebounce" in body or "setTimeout" in body


def test_schema_valid_badge_states(index_html: str) -> None:
    """devUpdateSchemaValidation sets badge to valid/invalid/parse error."""
    body = _extract_func(index_html, "devUpdateSchemaValidation")
    assert "'dev-validation-badge valid'" in body
    assert "'dev-validation-badge invalid'" in body
    assert "'parse error'" in body


def test_schema_errors_populated(index_html: str) -> None:
    """devUpdateSchemaValidation populates error panel with error details."""
    body = _extract_func(index_html, "devUpdateSchemaValidation")
    assert "errPanel" in body
    # Errors are iterated and appended
    assert "forEach" in body


def test_schema_preview_calls_buildform_with_target(index_html: str) -> None:
    """devUpdateSchemaPreview calls buildForm(schema, previewForm)."""
    body = _extract_func(index_html, "devUpdateSchemaPreview")
    assert "buildForm(schema, previewForm)" in body


def test_dev_new_schema_resets_to_starter(index_html: str) -> None:
    """devNewSchema resets editor content to DEV_STARTER_SCHEMA."""
    body = _extract_func(index_html, "devNewSchema")
    assert "DEV_STARTER_SCHEMA" in body


def test_dev_load_schema_file_accepts_json(index_html: str) -> None:
    """Load Schema file input accepts .json files."""
    assert 'accept=".json" id="devSchemaFileInput"' in index_html


def test_dev_format_schema_pretty_prints(index_html: str) -> None:
    """devFormatSchema uses 2-space indent for JSON.stringify."""
    body = _extract_func(index_html, "devFormatSchema")
    assert "JSON.stringify(obj, null, 2)" in body


def test_dev_save_schema_derives_filename(index_html: str) -> None:
    """devSaveSchema derives filename from schema title."""
    body = _extract_func(index_html, "devSaveSchema")
    assert "obj.title" in body
    assert ".json" in body


def test_schema_resizer_persists_ratio(index_html: str) -> None:
    """initDevResizer persists ratio to localStorage."""
    body = _extract_func(index_html, "initDevResizer")
    assert "formforge-dev-ratio-" in body
    assert "localStorage.setItem" in body


def test_schema_editor_in_split_pane(index_html: str) -> None:
    """Schema editor and preview are in the same dev-split container."""
    # The split pane should contain both editor and preview
    match = re.search(
        r'id="schemaSplit"([\s\S]*?)(?:</div>\s*){3,}',
        index_html,
    )
    assert match
    block = match.group(0)
    assert "schemaEditorPane" in block
    assert "schemaPreviewPane" in block


def test_schema_editor_wires_prism_json(index_html: str) -> None:
    """initSchemaEditor wires Prism.js JSON highlighting to CodeJar."""
    body = _extract_func(index_html, "initSchemaEditor")
    assert "devHighlightWithFolding" in body or "Prism.highlight" in body
    assert "Prism.languages.json" in body
    assert "CodeJar" in body


# ============================================================
#  ISSUE #118 — Context menu system
# ============================================================


def test_context_menu_prevents_default(index_html: str) -> None:
    """Schema editor contextmenu handler calls preventDefault."""
    body = _extract_func(index_html, "initSchemaEditor")
    assert "e.preventDefault()" in body
    assert "contextmenu" in body


def test_context_menu_four_submenus(index_html: str) -> None:
    """devSchemaContextItems returns 4 grouped submenus."""
    body = _extract_func(index_html, "devSchemaContextItems")
    assert "'Input Fields'" in body
    assert "'Choice Fields'" in body
    assert "'Complex Fields'" in body
    assert "'Layout'" in body


_INPUT_SUBMENU_TYPES = [
    "Text",
    "Email",
    "Phone",
    "Number",
    "Currency",
    "URL",
    "Date",
    "Time",
    "DateTime",
    "Textarea",
    "Long Text",
]


@pytest.mark.parametrize("label", _INPUT_SUBMENU_TYPES)
def test_input_submenu_entry(index_html: str, label: str) -> None:
    body = _extract_func(index_html, "devSchemaContextItems")
    assert f"'{label}'" in body or f'"{label}"' in body


_CHOICE_SUBMENU_TYPES = ["Select", "Multi Select", "Radio", "Checkbox", "Toggle"]


@pytest.mark.parametrize("label", _CHOICE_SUBMENU_TYPES)
def test_choice_submenu_entry(index_html: str, label: str) -> None:
    body = _extract_func(index_html, "devSchemaContextItems")
    assert f"'{label}'" in body or f'"{label}"' in body


_COMPLEX_SUBMENU_TYPES = ["Address", "Repeater", "File", "Signature", "List"]


@pytest.mark.parametrize("label", _COMPLEX_SUBMENU_TYPES)
def test_complex_submenu_entry(index_html: str, label: str) -> None:
    body = _extract_func(index_html, "devSchemaContextItems")
    assert f"'{label}'" in body or f'"{label}"' in body


_LAYOUT_SUBMENU_TYPES = ["Heading", "Hidden"]


@pytest.mark.parametrize("label", _LAYOUT_SUBMENU_TYPES)
def test_layout_submenu_entry(index_html: str, label: str) -> None:
    body = _extract_func(index_html, "devSchemaContextItems")
    assert f"'{label}'" in body or f'"{label}"' in body


def test_add_section_menu_item(index_html: str) -> None:
    body = _extract_func(index_html, "devSchemaContextItems")
    assert "'Add Section'" in body


def test_wrap_in_wizard_menu_item(index_html: str) -> None:
    body = _extract_func(index_html, "devSchemaContextItems")
    assert "'Wrap in Wizard'" in body


def test_insert_section_creates_unique_ids(index_html: str) -> None:
    """devInsertSection generates unique field IDs."""
    body = _extract_func(index_html, "devInsertSection")
    assert "allIds.has(f.id)" in body
    assert "f.id + '_' + i" in body or "f.id + '_'" in body


def test_wrap_in_wizard_adds_wizard_and_steps(index_html: str) -> None:
    """devWrapInWizard sets wizard: true and step numbers."""
    body = _extract_func(index_html, "devWrapInWizard")
    assert "schema.wizard = true" in body
    assert "s.step = i + 1" in body


def test_insert_snippet_appends_to_last_section(index_html: str) -> None:
    """devInsertSnippet adds field to the last section."""
    body = _extract_func(index_html, "devInsertSnippet")
    assert (
        "sections[schema.sections.length - 1]" in body or "sections.length - 1" in body
    )


def test_insert_snippet_deduplicates_ids(index_html: str) -> None:
    """devInsertSnippet appends numeric suffix for duplicate IDs."""
    body = _extract_func(index_html, "devInsertSnippet")
    assert "allIds.has(snip.id)" in body
    assert "snip.id + '_'" in body


def test_insert_snippet_triggers_preview(index_html: str) -> None:
    """devInsertSnippet calls devUpdateSchemaPreview after insert."""
    body = _extract_func(index_html, "devInsertSnippet")
    assert "devUpdateSchemaPreview()" in body


def test_template_editor_has_context_menu(index_html: str) -> None:
    """Template editor has contextmenu handler with template snippets."""
    body = _extract_func(index_html, "initTemplateEditor")
    assert "contextmenu" in body
    assert "devTemplateContextItems" in body


def test_context_menu_closes_on_click_outside(index_html: str) -> None:
    """Context menu closes on mousedown outside the menu."""
    assert "if (!e.target.closest('.ctx-menu')) hideContextMenu()" in index_html


def test_context_menu_closes_on_escape(index_html: str) -> None:
    """Context menu closes on Escape key via keyboard handler."""
    # Escape handling lives in ctxMenuHandleKeydown and the global keydown listener
    assert "hideContextMenu()" in index_html
    assert "'Escape'" in index_html


def test_context_menu_viewport_clamped(index_html: str) -> None:
    """showContextMenu clamps position to viewport edges."""
    body = _extract_func(index_html, "showContextMenu")
    assert "window.innerWidth" in body
    assert "window.innerHeight" in body
    assert "Math.max(0" in body


def test_insert_snippet_invalid_json_toast(index_html: str) -> None:
    """devInsertSnippet shows toast when JSON is invalid."""
    body = _extract_func(index_html, "devInsertSnippet")
    assert "Cannot insert" in body
    assert "fix JSON errors first" in body


# ============================================================
#  ISSUE #119 — Template Builder with DOCX preview
# ============================================================


def test_template_editor_loads_starter_on_init(index_html: str) -> None:
    """initTemplateEditor loads DEV_STARTER_TEMPLATE on first open."""
    body = _extract_func(index_html, "initTemplateEditor")
    assert "DEV_STARTER_TEMPLATE" in body


def test_template_editor_wires_prism_python(index_html: str) -> None:
    """initTemplateEditor uses Prism.js Python highlighting."""
    body = _extract_func(index_html, "initTemplateEditor")
    assert "devHighlightWithFolding" in body or "Prism.highlight" in body
    assert "Prism.languages.python" in body
    assert "CodeJar" in body


def test_sample_data_panel_collapsible(index_html: str) -> None:
    """Sample data panel has collapsed class and toggle function."""
    assert 'class="dev-sample-body collapsed"' in index_html
    assert "function devToggleSampleData" in index_html


def test_sample_data_toggle_arrow_rotates(index_html: str) -> None:
    """Toggle arrow gets 'expanded' class for rotation."""
    body = _extract_func(index_html, "devToggleSampleData")
    assert "expanded" in body


def test_sample_data_editor_wired_to_codejar(index_html: str) -> None:
    """initTemplateEditor also initializes sample data editor with CodeJar."""
    body = _extract_func(index_html, "initTemplateEditor")
    assert "sampleDataEditor" in body
    assert "sampleJar" in body or "CodeJar" in body


def test_devrunpreview_pipeline_stages(index_html: str) -> None:
    """devRunPreview updates badge through named stages."""
    body = _extract_func(index_html, "devRunPreview")
    assert "'loading Pyodide...'" in body
    assert "'loading template...'" in body
    assert "'generating DOCX...'" in body
    assert "'rendering preview...'" in body
    assert "'success'" in body


def test_devrunpreview_calls_mammoth(index_html: str) -> None:
    """devRunPreview uses mammoth.convertToHtml for DOCX-to-HTML."""
    body = _extract_func(index_html, "devRunPreview")
    assert "mammoth.convertToHtml" in body


def test_devrunpreview_uses_dompurify(index_html: str) -> None:
    """devRunPreview sanitizes mammoth output via DOMPurify."""
    body = _extract_func(index_html, "devRunPreview")
    assert "DOMPurify.sanitize" in body


def test_dompurify_cdn_loaded(index_html: str) -> None:
    """DOMPurify is loaded from CDN for HTML sanitization."""
    assert "dompurify@" in index_html


def test_docx_preview_white_background_css(index_html: str) -> None:
    """DOCX preview container has white background and Calibri font."""
    assert "dev-docx-preview" in index_html
    # Find the CSS rule containing the background (not the scrollbar override)
    matches = re.findall(r"\.dev-docx-preview\s*\{([^}]+)\}", index_html)
    css = " ".join(matches)
    assert "#ffffff" in css
    assert "Calibri" in css


def test_devrunpreview_error_uses_textcontent(index_html: str) -> None:
    """devRunPreview error display uses textContent, not innerHTML."""
    body = _extract_func(index_html, "devRunPreview")
    assert "errDiv.textContent" in body
    assert "errDiv.innerHTML" not in body


def test_devrunpreview_invalid_sample_data_guard(index_html: str) -> None:
    """devRunPreview catches invalid sample data JSON."""
    body = _extract_func(index_html, "devRunPreview")
    assert "Sample data is not valid JSON" in body


def test_devrunpreview_uses_pyodide_topy(index_html: str) -> None:
    """devRunPreview passes data via pyodide.toPy() + globals.set()."""
    body = _extract_func(index_html, "devRunPreview")
    assert "pyodide.toPy(" in body
    assert "pyodide.globals.set(" in body
    assert "pyodide.globals.delete(" in body


def test_devrunpreview_calls_loadbasemodule_silent(index_html: str) -> None:
    """devRunPreview calls loadBaseModule with silent: true to skip overlay."""
    body = _extract_func(index_html, "devRunPreview")
    assert "silent: true" in body or "silent:true" in body


def test_devrunpreview_shows_stencils_badge(index_html: str) -> None:
    """devRunPreview updates status badge to 'loading stencils...' during load."""
    body = _extract_func(index_html, "devRunPreview")
    assert "loading stencils" in body


def test_loadbasemodule_has_silent_param(index_html: str) -> None:
    """loadBaseModule accepts a silent option to suppress the loading overlay."""
    body = _extract_func(index_html, "loadBaseModule")
    assert "silent" in body
    assert "showOverlay" in body
    assert "hideOverlay" in body


def test_loadbasemodule_hides_overlay_in_finally(index_html: str) -> None:
    """loadBaseModule calls hideOverlay in a finally block for non-silent mode."""
    body = _extract_func(index_html, "loadBaseModule")
    assert "finally" in body
    assert "hideOverlay" in body


def test_dev_new_template_resets_to_starter(index_html: str) -> None:
    """devNewTemplate resets content to DEV_STARTER_TEMPLATE."""
    body = _extract_func(index_html, "devNewTemplate")
    assert "DEV_STARTER_TEMPLATE" in body


def test_dev_load_template_accepts_py(index_html: str) -> None:
    """Load Template file input accepts .py files."""
    assert 'accept=".py" id="devTemplateFileInput"' in index_html


def test_dev_save_template_filename(index_html: str) -> None:
    """devSaveTemplate downloads as template.py."""
    body = _extract_func(index_html, "devSaveTemplate")
    assert "'template.py'" in body


def test_template_snippets_defined(index_html: str) -> None:
    """TEMPLATE_SNIPPETS array is defined with stencils helpers."""
    assert "const TEMPLATE_SNIPPETS" in index_html
    assert "'Import stencils'" in index_html
    assert "'generate_docx scaffold'" in index_html
    assert "'table_section'" in index_html
    assert "'finalize'" in index_html


# ============================================================
#  ISSUE #120 — Local Workspace mode
# ============================================================


def test_workspace_fsaa_feature_detect_hides_button(index_html: str) -> None:
    """Boot hides Open Folder button if FSAA not supported."""
    assert "!window.showDirectoryPicker" in index_html
    assert "btnOpenFolderSetup" in index_html


def test_workspace_reads_schemas_and_templates(index_html: str) -> None:
    """devReadWorkspaceFromHandle reads schemas/ and templates/ dirs."""
    body = _extract_func(index_html, "devReadWorkspaceFromHandle")
    assert "'schemas'" in body or '"schemas"' in body
    assert "'templates'" in body or '"templates"' in body
    assert "_schema.spec.json" in body  # excluded
    assert "stencils.py" in body  # excluded


def test_workspace_load_schema_switches_tab(index_html: str) -> None:
    """devLoadWorkspaceFile routes schema to dev-schema tab."""
    body = _extract_func(index_html, "devLoadWorkspaceFile")
    assert "showTab('dev-schema')" in body


def test_workspace_load_template_switches_tab(index_html: str) -> None:
    """devLoadWorkspaceFile routes template to dev-template tab."""
    body = _extract_func(index_html, "devLoadWorkspaceFile")
    assert "showTab('dev-template')" in body


def test_workspace_polling_interval(index_html: str) -> None:
    """Workspace polling uses setInterval with a reasonable interval."""
    body = _extract_func(index_html, "devReadWorkspaceFromHandle")
    assert "5000" in body
    assert "setInterval" in body


def test_workspace_poll_auto_reloads_editor(index_html: str) -> None:
    """devPollWorkspace reloads changed file into active editor."""
    body = _extract_func(index_html, "devPollWorkspace")
    assert "devSchemaText = text" in body or "schemaJar" in body
    assert "devTemplateText = text" in body or "templateJar" in body


# ============================================================
#  ISSUE #121 — Mobile gate
# ============================================================


def test_mobile_gate_hides_dev_nav(index_html: str) -> None:
    """Dev nav is hidden at max-width 768px via CSS."""
    # The @media block contains multiple rules; use [\s\S] to span across them
    pattern = r"@media\s*\(max-width:\s*768px\)\s*\{[\s\S]*?\.dev-nav\s*\{\s*display:\s*none\s*!important"
    assert re.search(pattern, index_html), (
        "dev-nav must be display:none!important at <=768px"
    )


# ============================================================
#  ISSUE #122 — Regression: user mode unchanged
# ============================================================


def test_buildform_fallback_to_dynamicform(index_html: str) -> None:
    """buildForm falls back to #dynamicForm when targetForm is not provided."""
    match = re.search(
        r"function buildForm\(schema, targetForm\)([\s\S]*?)^function ",
        index_html,
        re.M,
    )
    assert match
    body = match.group(1)
    assert "targetForm || document.getElementById('dynamicForm')" in body


def test_existing_callers_unchanged(index_html: str) -> None:
    """Existing buildForm callers pass only schema (no second arg)."""
    # launchDemo, launchLocal, launchForm all call buildForm(currentSchema)
    calls = re.findall(r"buildForm\(currentSchema\)", index_html)
    assert len(calls) >= 2, f"Expected >=2 single-arg buildForm calls, got {len(calls)}"


def test_showview_dirty_guard_scoped_to_form(index_html: str) -> None:
    """showView dirty guard only triggers when leaving the form view."""
    body = _extract_func(index_html, "showView")
    # Guard should check that we're leaving form view specifically
    assert "view-form" in body
    assert "formDirty" in body
    assert "confirm(" in body


def test_wizard_indicator_appended_to_form_target(index_html: str) -> None:
    """Wizard indicator is appended to the form element (which uses targetForm)."""
    match = re.search(
        r"function buildForm\(schema, targetForm\)([\s\S]*?)^function ",
        index_html,
        re.M,
    )
    assert match
    body = match.group(1)
    assert "form.appendChild(indicator)" in body


def test_existing_test_count(index_html: str) -> None:
    """Verify the project has the expected pre-existing test files."""
    test_dir = Path(__file__).resolve().parent
    test_files = sorted(p.name for p in test_dir.glob("test_*.py"))
    assert "test_schemas.py" in test_files
    assert "test_stencils.py" in test_files
    assert "test_templates.py" in test_files
    assert "test_dev_mode.py" in test_files


# ============================================================
# GitHub Workspace Integration (#125)
# ============================================================


class TestGitHubWorkspaceHTML:
    """HTML structure tests for GitHub workspace integration."""

    def test_connect_modal_triggers_exist(self, index_html: str) -> None:
        """Connect modal trigger function exists."""
        assert "devGhShowConnectModal()" in index_html

    def test_connect_modal_exists(self, index_html: str) -> None:
        """GitHub connect modal dialog exists."""
        assert 'id="ghConnectModal"' in index_html
        assert 'role="dialog"' in index_html

    def test_connect_modal_repo_input(self, index_html: str) -> None:
        """Modal has repository input field."""
        assert 'id="ghConnectRepo"' in index_html

    def test_connect_modal_token_input(self, index_html: str) -> None:
        """Modal has password-type token input for security."""
        assert 'id="ghConnectToken"' in index_html
        assert 'type="password"' in index_html

    def test_connect_modal_branch_input(self, index_html: str) -> None:
        """Modal has optional branch input."""
        assert 'id="ghConnectBranch"' in index_html

    def test_connect_button_in_modal(self, index_html: str) -> None:
        """Connect button exists in the modal."""
        assert 'id="btnGhConnect"' in index_html

    def test_clear_token_button_exists(self, index_html: str) -> None:
        """Clear token button exists for security."""
        assert 'id="btnGhClearToken"' in index_html

    def test_new_branch_input_exists(self, index_html: str) -> None:
        """New branch name input exists."""
        assert 'id="ghNewBranchName"' in index_html

    def test_commit_panel_exists(self, index_html: str) -> None:
        """Commit panel with file list and message textarea exists."""
        assert 'id="ghCommitPanel"' in index_html
        assert 'id="ghCommitFileList"' in index_html
        assert 'id="ghCommitMsg"' in index_html

    def test_commit_push_button_exists(self, index_html: str) -> None:
        """Commit & Push button exists."""
        assert 'id="btnGhCommitPush"' in index_html

    def test_disconnect_button_calls_disconnect(self, index_html: str) -> None:
        """Disconnect button calls devGhDisconnect."""
        assert "devGhDisconnect()" in index_html

    def test_security_warning_in_modal(self, index_html: str) -> None:
        """Security warning about token scope is shown in connect modal."""
        assert "gh-connect-warning" in index_html
        assert "fine-grained personal access token" in index_html


class TestGitHubWorkspaceSVGIcons:
    """SVG icon tests for GitHub workspace."""

    def test_git_branch_icon_exists(self, index_html: str) -> None:
        assert 'id="icon-git-branch"' in index_html

    def test_git_commit_icon_exists(self, index_html: str) -> None:
        assert 'id="icon-git-commit"' in index_html

    def test_unlink_icon_exists(self, index_html: str) -> None:
        assert 'id="icon-unlink"' in index_html


class TestGitHubWorkspaceCSS:
    """CSS class tests for GitHub workspace."""

    @pytest.mark.parametrize(
        "css_class",
        [
            "gh-connect-modal",
            "gh-connect-panel",
            "gh-connect-field",
            "gh-connect-actions",
            "gh-connect-warning",
            "gh-toolbar",
            "gh-branch-select",
            "gh-commit-panel",
            "gh-commit-file-list",
            "gh-commit-file-entry",
            "gh-commit-msg",
            "gh-commit-actions",
            "gh-new-branch-row",
        ],
    )
    def test_css_class_defined(self, index_html: str, css_class: str) -> None:
        """All GitHub workspace CSS classes are defined in the stylesheet."""
        assert f".{css_class}" in index_html


class TestGitHubWorkspaceJavaScript:
    """JavaScript function and pattern tests for GitHub workspace."""

    def test_state_variables_exist(self, index_html: str) -> None:
        """GitHub workspace state variables are declared."""
        assert "contentSourceType" in index_html
        assert "ghOwner" in index_html
        assert "ghRepo" in index_html
        assert "ghBranch" in index_html
        assert "ghToken" in index_html
        assert "ghBranches" in index_html
        assert "ghOriginalContents" in index_html
        assert "ghModifiedFiles" in index_html

    def test_token_localstorage_key(self, index_html: str) -> None:
        """Token uses the correct localStorage key."""
        assert "formforge-dev-github-token" in index_html

    def test_repo_localstorage_key(self, index_html: str) -> None:
        """Repo info uses the correct localStorage key."""
        assert "formforge-dev-github-repo" in index_html

    def test_token_stored_in_localstorage(self, index_html: str) -> None:
        """Token localStorage key is referenced (migration or retrieval)."""
        assert "localStorage.getItem('formforge-dev-github-token')" in index_html

    def test_token_removed_on_clear(self, index_html: str) -> None:
        """Token is removed from localStorage on clear."""
        assert "localStorage.removeItem('formforge-dev-github-token')" in index_html

    def test_github_api_repo_url_pattern(self, index_html: str) -> None:
        """GitHub API URL pattern for repo info is present."""
        assert "api.github.com/repos/" in index_html

    def test_github_api_contents_url_pattern(self, index_html: str) -> None:
        """GitHub Contents API URL pattern is present (for fetching files)."""
        assert "/contents/schemas" in index_html
        assert "/contents/templates" in index_html

    def test_github_api_branches_url_pattern(self, index_html: str) -> None:
        """GitHub API branches endpoint is used."""
        assert "/branches" in index_html

    def test_contents_api_put_pattern(self, index_html: str) -> None:
        """Contents API PUT is used for single-file commits."""
        match = re.search(r"method:\s*['\"]PUT['\"]", index_html)
        assert match, "PUT method for Contents API not found"

    def test_git_trees_api_pattern(self, index_html: str) -> None:
        """Git Trees API is used for atomic multi-file commits."""
        assert "/git/trees" in index_html

    def test_git_commits_api_pattern(self, index_html: str) -> None:
        """Git Commits API is used for atomic multi-file commits."""
        assert "/git/commits/" in index_html

    def test_git_refs_api_pattern(self, index_html: str) -> None:
        """Git Refs API is used for branch operations."""
        assert "/git/refs/heads/" in index_html
        assert "/git/refs" in index_html

    def test_git_blobs_api_pattern(self, index_html: str) -> None:
        """Git Blobs API is used for creating file blobs."""
        assert "/git/blobs" in index_html

    def test_create_branch_uses_post(self, index_html: str) -> None:
        """Branch creation uses POST to git/refs."""
        # Find devGhCreateBranch function body
        match = re.search(
            r"async function devGhCreateBranch\(\)([\s\S]*?)^(?:async )?function ",
            index_html,
            re.M,
        )
        assert match
        body = match.group(1)
        assert "refs/heads/" in body
        assert "'POST'" in body or '"POST"' in body

    def test_file_modification_tracking(self, index_html: str) -> None:
        """devGhTrackModification compares current vs original content."""
        match = re.search(
            r"function devGhTrackModification\(type, index\)([\s\S]*?)^(?:async )?function ",
            index_html,
            re.M,
        )
        assert match
        body = match.group(1)
        assert "ghOriginalContents" in body
        assert "ghModifiedFiles" in body

    def test_conflict_409_handling(self, index_html: str) -> None:
        """409 conflict error is handled in commit function."""
        match = re.search(
            r"async function devGhCommitAndPush\(\)([\s\S]*?)^(?:async )?function ",
            index_html,
            re.M,
        )
        assert match
        body = match.group(1)
        assert "'409'" in body or '"409"' in body

    def test_disconnect_clears_state(self, index_html: str) -> None:
        """devGhDisconnect resets all GitHub workspace state."""
        match = re.search(
            r"function devGhDisconnect\(\)([\s\S]*?)^(?:async )?function ",
            index_html,
            re.M,
        )
        assert match
        body = match.group(1)
        assert "contentSourceType = null" in body
        assert "ghOwner = ''" in body
        assert "ghModifiedFiles" in body

    def test_schema_editor_tracks_modifications(self, index_html: str) -> None:
        """Schema editor onUpdate hook calls modification tracker."""
        assert "devGhTrackModification('schema'" in index_html

    def test_template_editor_tracks_modifications(self, index_html: str) -> None:
        """Template editor onUpdate hook calls modification tracker."""
        assert "devGhTrackModification('template'" in index_html

    def test_repo_url_parser_handles_full_urls(self, index_html: str) -> None:
        """devGhParseRepoInput handles GitHub URLs."""
        assert "github.com" in index_html
        match = re.search(
            r"function devGhParseRepoInput\(input\)([\s\S]*?)^(?:async )?function ",
            index_html,
            re.M,
        )
        assert match
        body = match.group(1)
        # The function uses a regex with escaped dot: github\\.com
        assert "github" in body
        assert "urlMatch" in body

    def test_token_authorization_header(self, index_html: str) -> None:
        """Token is sent via Authorization header, not URL params."""
        match = re.search(
            r"function ghHeaders\(\)([\s\S]*?)^(?:async )?function ",
            index_html,
            re.M,
        )
        assert match
        body = match.group(1)
        assert "Authorization" in body
        assert "token " in body

    def test_modal_close_on_escape(self, index_html: str) -> None:
        """Connect modal has Escape key handler."""
        assert "devGhCloseConnectModal" in index_html

    def test_excludes_spec_and_stencils(self, index_html: str) -> None:
        """File fetching excludes _schema.spec.json and stencils.py."""
        match = re.search(
            r"async function devGhFetchFiles\(\)([\s\S]*?)^(?:async )?function ",
            index_html,
            re.M,
        )
        assert match
        body = match.group(1)
        assert "_schema.spec.json" in body
        assert "stencils.py" in body

    def test_branch_name_validation(self, index_html: str) -> None:
        """Branch name input has validation pattern."""
        match = re.search(
            r"async function devGhCreateBranch\(\)([\s\S]*?)^(?:async )?function ",
            index_html,
            re.M,
        )
        assert match
        body = match.group(1)
        # Check for regex validation of branch name
        assert "test(name)" in body or "test(" in body


# ============================================================
#  ISSUE #130 — Line Numbers in Editors
# ============================================================


def test_schema_line_numbers_element(index_html: str) -> None:
    """Schema editor has a line numbers gutter element."""
    assert 'id="schemaLineNumbers"' in index_html


def test_template_line_numbers_element(index_html: str) -> None:
    """Template editor has a line numbers gutter element."""
    assert 'id="templateLineNumbers"' in index_html


def test_sample_line_numbers_element(index_html: str) -> None:
    """Sample data editor has a line numbers gutter element."""
    assert 'id="sampleLineNumbers"' in index_html


def test_editor_wrap_css_class(index_html: str) -> None:
    """CSS class .dev-editor-wrap exists."""
    assert ".dev-editor-wrap" in index_html


def test_line_numbers_css_class(index_html: str) -> None:
    """CSS class .dev-line-numbers exists with user-select: none."""
    assert ".dev-line-numbers" in index_html
    match = re.search(r"\.dev-line-numbers\s*\{([^}]+)\}", index_html)
    assert match
    assert "user-select: none" in match.group(1)


def test_scroll_sync_schema_editor(index_html: str) -> None:
    """Schema editor has scroll sync for line numbers."""
    body = _extract_func(index_html, "initSchemaEditor")
    assert "'scroll'" in body
    assert "gutterEl.scrollTop" in body or "scrollTop" in body


def test_scroll_sync_template_editor(index_html: str) -> None:
    """Template editor has scroll sync for line numbers."""
    body = _extract_func(index_html, "initTemplateEditor")
    assert "'scroll'" in body
    assert "tplGutter.scrollTop" in body or "scrollTop" in body


def test_fold_toggle_css_class(index_html: str) -> None:
    """CSS class .dev-fold-toggle exists."""
    assert ".dev-fold-toggle" in index_html


def test_fold_regions_detects_json(index_html: str) -> None:
    """devFindFoldRegions handles JSON language."""
    body = _extract_func(index_html, "devFindFoldRegions")
    assert "'json'" in body or '"json"' in body


def test_fold_regions_detects_python(index_html: str) -> None:
    """devFindFoldRegions handles Python language."""
    body = _extract_func(index_html, "devFindFoldRegions")
    assert "'python'" in body or '"python"' in body


def test_fold_state_variable(index_html: str) -> None:
    """devFoldState Map variable exists."""
    assert "devFoldState" in index_html


def test_highlight_applies_fold_placeholder(index_html: str) -> None:
    """devHighlightWithFolding inserts fold placeholders and hides folded lines."""
    body = _extract_func(index_html, "devHighlightWithFolding")
    assert "dev-fold-placeholder" in body
    assert "hiddenLines" in body


def test_editors_use_fold_highlighting(index_html: str) -> None:
    """All three CodeJar editors use devHighlightWithFolding."""
    assert "devHighlightWithFolding(editor, Prism.languages.json" in index_html
    assert "devHighlightWithFolding(editor, Prism.languages.python" in index_html


def test_edit_clears_folds(index_html: str) -> None:
    """Editing in any editor clears fold state to prevent data loss."""
    schema_body = _extract_func(index_html, "initSchemaEditor")
    assert "folds.clear()" in schema_body or "clear()" in schema_body
    template_body = _extract_func(index_html, "initTemplateEditor")
    assert "folds.clear()" in template_body or "clear()" in template_body


# ============================================================
#  ISSUE #131 — Keyboard Shortcuts
# ============================================================


def test_comment_toggle_python(index_html: str) -> None:
    """Keyboard handler has Python comment toggle logic."""
    body = _extract_func(index_html, "devEditorKeydownHandler")
    assert "'# '" in body or '"# "' in body


def test_move_line_alt_arrows(index_html: str) -> None:
    """Keyboard handler checks altKey with ArrowUp/ArrowDown and supports multi-line."""
    body = _extract_func(index_html, "devEditorKeydownHandler")
    assert "altKey" in body
    assert "ArrowUp" in body
    assert "ArrowDown" in body
    assert "firstLine" in body and "lastLine" in body  # multi-line support


def _extract_global_keydown(html: str) -> str:
    """Extract handleGlobalKeydown body (ends at window.addEventListener)."""
    match = re.search(
        r"function handleGlobalKeydown\b[^{]*\{([\s\S]*?)^(?:window\.|//\s*=)",
        html,
        re.M,
    )
    assert match, "handleGlobalKeydown not found"
    return match.group(1)


def test_ctrl_s_dev_mode_schema(index_html: str) -> None:
    """Global handler routes Ctrl+S to devSaveSchema in dev mode."""
    body = _extract_global_keydown(index_html)
    assert "devSaveSchema" in body


def test_ctrl_s_dev_mode_template(index_html: str) -> None:
    """Global handler routes Ctrl+S to devSaveTemplate in dev mode."""
    body = _extract_global_keydown(index_html)
    assert "devSaveTemplate" in body


def test_ctrl_enter_dev_mode_preview(index_html: str) -> None:
    """Global handler routes Ctrl+Enter to devRunPreview in dev mode."""
    body = _extract_global_keydown(index_html)
    assert "devRunPreview" in body


def test_schema_save_button_title(index_html: str) -> None:
    """Schema save button has shortcut title attribute."""
    assert re.search(
        r'onclick="devSaveSchema\(\)"[^>]*title="[^"]*Ctrl\+S',
        index_html,
    )


def test_template_save_button_title(index_html: str) -> None:
    """Template save button has shortcut title attribute."""
    assert re.search(
        r'onclick="devSaveTemplate\(\)"[^>]*title="[^"]*Ctrl\+S',
        index_html,
    )


def test_preview_button_title(index_html: str) -> None:
    """Preview DOCX button has shortcut title attribute."""
    assert re.search(
        r'onclick="devRunPreview\(\)"[^>]*title="[^"]*Ctrl\+Enter',
        index_html,
    )


# ============================================================
#  ISSUE #132 — Auto-Generated Sample Data
# ============================================================


def test_sample_data_generators_object(index_html: str) -> None:
    """SAMPLE_DATA_GENERATORS object exists."""
    assert "SAMPLE_DATA_GENERATORS" in index_html


def test_auto_fill_button_exists(index_html: str) -> None:
    """Auto-fill button exists in HTML."""
    assert "devAutoFillSampleData()" in index_html


def test_generators_cover_field_types(index_html: str) -> None:
    """Generators cover key field types."""
    match = re.search(
        r"const SAMPLE_DATA_GENERATORS\s*=\s*\{([\s\S]*?)\n\};",
        index_html,
    )
    assert match
    body = match.group(1)
    for ft in [
        "text",
        "email",
        "tel",
        "number",
        "currency",
        "address",
        "repeater",
        "select",
        "checkbox",
        "toggle",
        "hidden",
    ]:
        assert f"  {ft}:" in body or f"  {ft} :" in body, f"Generator missing for {ft}"


def test_auto_sync_on_first_use(index_html: str) -> None:
    """devUpdateSchemaPreview auto-fills sample data when empty."""
    body = _extract_func(index_html, "devUpdateSchemaPreview")
    assert "devGenerateSampleData" in body


# ============================================================
#  ISSUE #133 — Schema-Template Cross-Awareness
# ============================================================


def test_parsed_schema_set_on_valid(index_html: str) -> None:
    """devUpdateSchemaValidation sets devParsedSchema on valid parse."""
    body = _extract_func(index_html, "devUpdateSchemaValidation")
    assert "devParsedSchema = schema" in body


def test_parsed_schema_cleared_on_invalid(index_html: str) -> None:
    """devUpdateSchemaValidation clears devParsedSchema on invalid parse."""
    body = _extract_func(index_html, "devUpdateSchemaValidation")
    assert "devParsedSchema = null" in body


def test_template_context_uses_parsed_schema(index_html: str) -> None:
    """devTemplateContextItems references devParsedSchema."""
    body = _extract_func(index_html, "devTemplateContextItems")
    assert "devParsedSchema" in body


def test_coverage_badge_element(index_html: str) -> None:
    """Schema preview header has coverage badge element."""
    assert 'id="schemaCoverageBadge"' in index_html


def test_coverage_badge_updated(index_html: str) -> None:
    """devUpdateSchemaPreview updates coverage badge."""
    body = _extract_func(index_html, "devUpdateSchemaPreview")
    assert "schemaCoverageBadge" in body
    assert "devCountTemplateFieldRefs" in body


# ============================================================
#  ISSUE #134 — Smart Save
# ============================================================


def test_save_schema_checks_workspace(index_html: str) -> None:
    """devSaveSchema checks workspaceHandle before downloading."""
    body = _extract_func(index_html, "devSaveSchema")
    assert "workspaceHandle" in body
    assert "currentWorkspaceFile" in body


def test_save_template_checks_workspace(index_html: str) -> None:
    """devSaveTemplate checks workspaceHandle before downloading."""
    body = _extract_func(index_html, "devSaveTemplate")
    assert "workspaceHandle" in body
    assert "currentWorkspaceFile" in body


# --- Custom Scrollbars (#139) ---


def test_webkit_scrollbar_styles(index_html: str) -> None:
    """Custom WebKit scrollbar pseudo-elements should be defined."""
    assert "::-webkit-scrollbar " in index_html or "::-webkit-scrollbar{" in index_html
    assert "::-webkit-scrollbar-thumb" in index_html
    assert "::-webkit-scrollbar-track" in index_html


def test_firefox_scrollbar_styles(index_html: str) -> None:
    """Firefox scrollbar properties should be set."""
    assert "scrollbar-width: thin" in index_html
    assert "scrollbar-color:" in index_html


def test_docx_preview_scrollbar_override(index_html: str) -> None:
    """DOCX preview should have light scrollbar colors for its white background."""
    assert ".dev-docx-preview::-webkit-scrollbar-thumb" in index_html
    assert ".dev-docx-preview::-webkit-scrollbar-track" in index_html


def test_dev_pane_scrollbar_fade(index_html: str) -> None:
    """Dev Mode panes should fade scrollbar when not hovering."""
    assert ".dev-pane:hover::-webkit-scrollbar-thumb" in index_html
    assert ".dev-editor:hover::-webkit-scrollbar-thumb" in index_html


# --- Navigation & Organization (#137) ---


def test_back_button_label(index_html: str) -> None:
    """Back button in form view should say 'Back', not 'Back to picker'."""
    pattern = re.compile(r'<button[^>]*class="btn-back"[^>]*>.*?</button>', re.DOTALL)
    match = pattern.search(index_html)
    assert match, "btn-back button not found"
    btn_text = re.sub(r"<[^>]+>", "", match.group()).strip()
    assert btn_text == "Back", f"Expected 'Back', got '{btn_text}'"


def test_dev_docs_tab_exists(index_html: str) -> None:
    """Nav should have a Docs tab."""
    assert 'id="tab-dev-docs"' in index_html
    assert 'data-tab="dev-docs"' in index_html


def test_dev_docs_view_exists(index_html: str) -> None:
    """A dev-docs view panel should exist."""
    assert 'id="view-dev-docs"' in index_html


def test_dev_docs_contains_doc_cards(index_html: str) -> None:
    """All four doc cards should be inside the dev-docs view."""
    start = index_html.index('id="view-dev-docs"')
    for doc_id in ["schemaGuide", "templateGuide", "fieldTypes", "exampleSchema"]:
        pos = index_html.index(f'id="{doc_id}"', start)
        assert pos > start, f"{doc_id} should be inside the dev-docs view"


def test_dev_docs_in_valid_tabs(index_html: str) -> None:
    """dev-docs should be in VALID_TABS."""
    assert "'dev-docs'" in index_html or '"dev-docs"' in index_html
    # Check it's in the Set definition
    assert "dev-docs" in index_html


def test_how_it_works_removed_from_setup(index_html: str) -> None:
    """The 'How It Works' card was removed to reduce clutter on the setup view."""
    setup_start = index_html.index('id="view-setup"')
    setup_end = index_html.index("<main", setup_start + 1)
    setup_html = index_html[setup_start:setup_end]
    assert "how-it-works-card" not in setup_html, (
        "How It Works card should not be in setup view"
    )


def test_profile_empty_state_hint(index_html: str) -> None:
    """Profile dropdown should show a helpful hint when empty."""
    assert "Save a profile to autofill common fields" in index_html


def test_picker_after_source_grid(index_html: str) -> None:
    """Picker section should appear after the source grid in setup view."""
    setup_start = index_html.index('id="view-setup"')
    setup_end = index_html.index("<main", setup_start + 1)
    setup_html = index_html[setup_start:setup_end]
    grid_pos = setup_html.index("source-grid")
    picker_pos = setup_html.index('id="pickerSection"')
    assert picker_pos > grid_pos, "Picker section should appear after source grid"


def test_local_files_collapsed_by_default(index_html: str) -> None:
    """Local Files card body should be collapsed by default."""
    assert 'id="localCardBody"' in index_html
    # The local-card-body should not have 'open' class by default
    start = index_html.index('id="localCardBody"')
    tag_start = index_html.rfind("<", 0, start)
    tag_end = index_html.index(">", start)
    tag = index_html[tag_start : tag_end + 1]
    assert "local-card-body" in tag
    assert "open" not in tag.split("class=")[1].split('"')[1], (
        "Local card body should not have 'open' class by default"
    )


def test_choose_a_form_heading(index_html: str) -> None:
    """Picker section should use 'Choose a Form' heading."""
    assert "Choose a Form" in index_html


def test_activity_log_label(index_html: str) -> None:
    """Console panel should be labeled 'Activity Log' not 'console output'."""
    assert "Activity Log" in index_html
    assert "console output" not in index_html


def test_console_panel_hidden_by_default(index_html: str) -> None:
    """Console panel should be hidden initially, shown when log entries are added."""
    start = index_html.index('id="consolePanel"')
    tag_start = index_html.rfind("<", 0, start)
    tag_end = index_html.index(">", start)
    tag = index_html[tag_start : tag_end + 1]
    assert "display:none" in tag, "Console panel should be hidden by default"


def test_picker_card_dblclick_handler(index_html: str) -> None:
    """Picker grid should have a dblclick event listener for quick launch."""
    body = _extract_func(index_html, "renderPicker")
    assert "dblclick" in body, "renderPicker should register a dblclick handler"
    assert "launchForm" in body, "dblclick handler should call launchForm"


def test_picker_auto_scroll_on_connect(index_html: str) -> None:
    """connectRepo should scroll the picker section into view after rendering."""
    body = _extract_func(index_html, "connectRepo")
    assert "scrollIntoView" in body, "connectRepo should scroll to picker"


def test_docs_not_on_setup_view(index_html: str) -> None:
    """Documentation cards should not be on the setup view."""
    setup_start = index_html.index('id="view-setup"')
    # Find the end of setup view (next <main)
    setup_end = index_html.index("<main", setup_start + 1)
    setup_html = index_html[setup_start:setup_end]
    assert 'id="docsSection"' not in setup_html, (
        "docsSection should not be in the setup view"
    )


# --- Wizard Preview Navigation Fix ---


def test_wizard_goto_accepts_form_param(index_html: str) -> None:
    """wizardGoTo should accept an optional formEl parameter."""
    body = _extract_func(index_html, "wizardGoTo")
    assert "formEl" in body, "wizardGoTo should accept formEl parameter"
    assert "dynamicForm" in body, "wizardGoTo should fall back to dynamicForm"


def test_wizard_next_accepts_form_param(index_html: str) -> None:
    """wizardNext should accept an optional formEl parameter."""
    body = _extract_func(index_html, "wizardNext")
    assert "formEl" in body, "wizardNext should accept formEl parameter"


def test_wizard_step_click_accepts_form_param(index_html: str) -> None:
    """wizardStepClick should accept an optional formEl parameter."""
    body = _extract_func(index_html, "wizardStepClick")
    assert "formEl" in body, "wizardStepClick should accept formEl parameter"


def test_wizard_goto_skips_submit_area_in_preview(index_html: str) -> None:
    """wizardGoTo should not touch .submit-area when operating on a preview form."""
    body = _extract_func(index_html, "wizardGoTo")
    assert "isPreview" in body, "wizardGoTo should detect preview mode"


def test_buildform_passes_form_to_wizard_handlers(index_html: str) -> None:
    """buildForm should pass the form container to wizard click handlers."""
    body = _extract_func(index_html, "buildForm")
    assert "wizardStepClick(i, form)" in body
    assert "wizardNext(sectionIdx, form)" in body
    assert "wizardGoTo(sectionIdx - 1, form)" in body


def test_buildform_skips_submit_area_for_preview(index_html: str) -> None:
    """buildForm should not touch .submit-area when rendering into a target form."""
    body = _extract_func(index_html, "buildForm")
    assert "if (!targetForm)" in body, (
        "submit-area toggle should be guarded by targetForm check"
    )


def test_wizard_step_drag_reorder_in_preview(index_html: str) -> None:
    """Wizard step indicators should support drag-to-reorder in preview."""
    body = _extract_func(index_html, "devEnablePreviewDragDrop")
    assert "wizard-indicator" in body, "should find the wizard indicator"
    assert "wizard-step" in body
    assert "dragstart" in body
    assert "devSyncSchemaFromPreview" in body


def test_wizard_add_buttons_scoped_to_active_step(index_html: str) -> None:
    """In wizard preview, add-section buttons should only show near the active step."""
    body = _extract_func(index_html, "devEnablePreviewDragDrop")
    assert "devUpdateWizardAddButtons" in body, (
        "should call devUpdateWizardAddButtons on initial render"
    )
    goto_body = _extract_func(index_html, "wizardGoTo")
    assert "devUpdateWizardAddButtons" in goto_body, (
        "should update add-button visibility on step change"
    )


def test_dev_update_wizard_add_buttons_function(index_html: str) -> None:
    """devUpdateWizardAddButtons should toggle display of .dev-section-add elements."""
    body = _extract_func(index_html, "devUpdateWizardAddButtons")
    assert "dev-section-add" in body
    assert "addIndex" in body


def test_wizard_step_drag_css(index_html: str) -> None:
    """CSS for wizard step drag indicators should exist."""
    assert ".wizard-step.dragging" in index_html
    assert ".wizard-step.drag-over-left" in index_html
    assert ".wizard-step.drag-over-right" in index_html


# ============================================================
#  ISSUE #88 — Accessibility (WCAG 2.1 AA)
# ============================================================


def test_overlay_sets_inert_on_show(index_html: str) -> None:
    """showOverlay should set inert on content behind the overlay."""
    match = re.search(
        r"function showOverlay\(msg\)([\s\S]*?)^function ",
        index_html,
        re.M,
    )
    assert match
    assert "inert" in match.group(1)


def test_overlay_removes_inert_on_hide(index_html: str) -> None:
    """hideOverlay should remove inert from content."""
    match = re.search(
        r"function hideOverlay\(\)([\s\S]*?)^(?:async )?function ",
        index_html,
        re.M,
    )
    assert match
    assert "removeAttribute('inert')" in match.group(1)


def test_prefers_reduced_motion_media_query(index_html: str) -> None:
    """CSS includes prefers-reduced-motion media query."""
    assert "prefers-reduced-motion: reduce" in index_html
    assert "animation-duration: 0.01ms" in index_html


def test_sample_data_toggle_aria_expanded(index_html: str) -> None:
    """Sample data toggle button has aria-expanded attribute."""
    match = re.search(r'class="dev-sample-toggle"[^>]*>', index_html)
    assert match
    assert "aria-expanded" in match.group(0)


def test_sample_data_toggle_updates_aria(index_html: str) -> None:
    """devToggleSampleData updates aria-expanded."""
    match = re.search(
        r"function devToggleSampleData\(\)([\s\S]*?)^(?:async )?function ",
        index_html,
        re.M,
    )
    assert match
    assert "aria-expanded" in match.group(1)


def test_forms_view_has_tabpanel_role(index_html: str) -> None:
    """Forms view (view-setup) should have role=tabpanel."""
    match = re.search(r'id="view-setup"[^>]*>', index_html)
    assert match
    assert 'role="tabpanel"' in match.group(0)
    assert 'aria-labelledby="tab-forms"' in match.group(0)


def test_demo_sets_content_source_type(index_html: str) -> None:
    """launchDemo should set contentSourceType to 'demo'."""
    match = re.search(
        r"async function launchDemo\(\)([\s\S]*?)^(?:async )?function ",
        index_html,
        re.M,
    )
    assert match
    assert "contentSourceType = 'demo'" in match.group(1)


def test_picker_uses_abort_controller(index_html: str) -> None:
    """renderPicker should use AbortController to prevent listener accumulation."""
    match = re.search(
        r"function renderPicker\(\)([\s\S]*?)^(?:async )?function ",
        index_html,
        re.M,
    )
    assert match
    body = match.group(1)
    assert "AbortController" in body
    assert "signal" in body


# ============================================================
#  ISSUE #157 — Git controls in editor tabs
# ============================================================


def test_git_toolbar_exists(index_html: str) -> None:
    """Git toolbar element exists with branch selector and controls."""
    assert 'id="ghToolbar"' in index_html
    assert 'id="ghBranchSelect"' in index_html
    assert 'id="ghToolbarRepo"' in index_html


def test_git_toolbar_has_disconnect_button(index_html: str) -> None:
    """Git toolbar has disconnect button."""
    match = re.search(r'id="ghToolbar"([\s\S]*?)</div>', index_html)
    assert match
    assert "devGhDisconnect()" in match.group(1)


def test_git_toolbar_has_new_branch_button(index_html: str) -> None:
    """Git toolbar has new branch button."""
    match = re.search(r'id="ghToolbar"([\s\S]*?)</div>', index_html)
    assert match
    assert "devGhShowNewBranch()" in match.group(1)


def test_git_toolbar_has_refresh_button(index_html: str) -> None:
    """Git toolbar has refresh button."""
    match = re.search(r'id="ghToolbar"([\s\S]*?)</div>', index_html)
    assert match
    assert "devGhRefreshFiles()" in match.group(1)


def test_update_git_toolbar_function(index_html: str) -> None:
    """updateGitToolbar shows/hides toolbar based on contentSourceType."""
    body = _extract_func(index_html, "updateGitToolbar")
    assert "contentSourceType" in body
    assert "'github'" in body
    assert "visible" in body


def test_template_source_toolbar_exists(index_html: str) -> None:
    """Template editor has a source toolbar like the schema editor."""
    assert 'id="templateSourceToolbar"' in index_html
    assert 'id="templateCommitBtn"' in index_html
    assert 'id="templateSaveLocalBtn"' in index_html


def test_connect_repo_updates_git_toolbar(index_html: str) -> None:
    """connectRepo calls updateGitToolbar after connecting."""
    body = _extract_func(index_html, "connectRepo")
    assert "updateGitToolbar()" in body


def test_disconnect_updates_git_toolbar(index_html: str) -> None:
    """devGhDisconnect calls updateGitToolbar after disconnecting."""
    body = _extract_func(index_html, "devGhDisconnect")
    assert "updateGitToolbar()" in body
