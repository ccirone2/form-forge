"""Tests for Dev Mode feature additions in index.html.

Since Dev Mode is client-side JavaScript, these tests validate:
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

INDEX_PATH = Path(__file__).resolve().parent.parent / "index.html"
SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"
SPEC_PATH = SCHEMAS_DIR / "_schema.spec.json"


@pytest.fixture(scope="module")
def index_html() -> str:
    return INDEX_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def spec() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


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


def test_mode_toggle_button_exists(index_html: str) -> None:
    assert 'id="modeToggle"' in index_html
    assert "toggleDevMode()" in index_html


def test_dev_nav_exists(index_html: str) -> None:
    assert 'id="devNav"' in index_html
    assert 'class="dev-nav-tab' in index_html


def test_dev_nav_has_three_tabs(index_html: str) -> None:
    assert index_html.count('class="dev-nav-tab') == 3


def test_view_dev_schema_exists(index_html: str) -> None:
    assert 'id="view-dev-schema"' in index_html


def test_view_dev_template_exists(index_html: str) -> None:
    assert 'id="view-dev-template"' in index_html


def test_view_dev_workspace_exists(index_html: str) -> None:
    assert 'id="view-dev-workspace"' in index_html


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


def test_workspace_drop_zone_exists(index_html: str) -> None:
    assert 'id="workspaceDropZone"' in index_html


def test_workspace_file_list_exists(index_html: str) -> None:
    assert 'id="workspaceFileList"' in index_html


# --- CSS Sections ---


def test_css_section_31_dev_mode_core(index_html: str) -> None:
    assert "31. DEV MODE CORE" in index_html


def test_css_section_32_split_pane(index_html: str) -> None:
    assert "32. DEV SPLIT PANE" in index_html


def test_css_section_33_context_menu(index_html: str) -> None:
    assert "33. CONTEXT MENU" in index_html


def test_css_section_34_template_builder(index_html: str) -> None:
    assert "34. TEMPLATE BUILDER" in index_html


def test_css_section_35_workspace(index_html: str) -> None:
    assert "35. WORKSPACE" in index_html


def test_css_section_36_mobile_gate(index_html: str) -> None:
    assert "36. DEV MODE MOBILE GATE" in index_html


def test_mobile_gate_hides_toggle(index_html: str) -> None:
    """The mode toggle must be disabled on narrow viewports."""
    # Find the @media block for 768px in section 36 — toggle is disabled via
    # pointer-events:none (shown but non-interactive) rather than display:none
    pattern = r"@media\s*\(max-width:\s*768px\)\s*\{[^}]*\.mode-toggle\s*\{"
    assert re.search(pattern, index_html), "mode-toggle must be gated at <=768px"


# --- JavaScript Functions ---


_REQUIRED_FUNCTIONS = [
    "toggleDevMode",
    "showDevTab",
    "handleDevModeResize",
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
    "devOpenWorkspace",
    "devReadWorkspaceFromHandle",
    "devRenderWorkspaceFiles",
    "devLoadWorkspaceFile",
    "devSaveToWorkspace",
    "devPollWorkspace",
    "devRefreshWorkspace",
    "initWorkspaceDropZone",
]


@pytest.mark.parametrize("func_name", _REQUIRED_FUNCTIONS)
def test_js_function_exists(index_html: str, func_name: str) -> None:
    assert f"function {func_name}" in index_html


# --- State Variables ---


_REQUIRED_STATE_VARS = [
    "devMode",
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


def test_boot_restores_dev_mode(index_html: str) -> None:
    assert "formforge-dev-mode" in index_html
    assert "localStorage.getItem('formforge-dev-mode')" in index_html


def test_boot_inits_workspace_drop_zone(index_html: str) -> None:
    assert "initWorkspaceDropZone()" in index_html


def test_boot_adds_resize_listener(index_html: str) -> None:
    assert "handleDevModeResize" in index_html
    assert "addEventListener('resize'" in index_html


# --- Dev tab whitelist ---


def test_valid_dev_tabs_whitelist(index_html: str) -> None:
    """VALID_DEV_TABS must contain all three dev tab names."""
    assert "VALID_DEV_TABS" in index_html
    assert "'dev-schema'" in index_html
    assert "'dev-template'" in index_html
    assert "'dev-workspace'" in index_html


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


def test_polling_stopped_on_dev_mode_exit(index_html: str) -> None:
    """toggleDevMode must clear the workspace poller when exiting."""
    match = re.search(
        r"function toggleDevMode\(\)([\s\S]*?)^function ", index_html, re.M
    )
    assert match
    body = match.group(1)
    assert "clearInterval(devWorkspacePoller)" in body


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
#  ISSUE #116 — Mode switch toggle
# ============================================================


def _extract_func(html: str, name: str) -> str:
    """Extract JS function body from index.html."""
    match = re.search(rf"function {name}\b[^{{]*\{{([\s\S]*?)^function ", html, re.M)
    assert match, f"Function {name} not found"
    return match.group(1)


def test_toggle_writes_localstorage(index_html: str) -> None:
    """toggleDevMode must write formforge-dev-mode to localStorage."""
    body = _extract_func(index_html, "toggleDevMode")
    assert "localStorage.setItem('formforge-dev-mode'" in body


def test_toggle_deactivation_returns_to_setup(index_html: str) -> None:
    """Toggling off must call showView('setup')."""
    body = _extract_func(index_html, "toggleDevMode")
    assert "showView('setup')" in body


def test_toggle_label_changes(index_html: str) -> None:
    """Toggle button label changes between 'Dev On' and 'Dev'."""
    body = _extract_func(index_html, "toggleDevMode")
    assert "'Dev On'" in body
    assert "'Dev'" in body


def test_toggle_active_class(index_html: str) -> None:
    """Toggle button adds/removes .active class."""
    body = _extract_func(index_html, "toggleDevMode")
    assert "classList.toggle('active'" in body


def test_toggle_shows_hides_dev_nav(index_html: str) -> None:
    """toggleDevMode shows/hides devNav."""
    body = _extract_func(index_html, "toggleDevMode")
    assert "devNav" in body
    assert "'flex'" in body
    assert "'none'" in body


def test_toggle_width_guard(index_html: str) -> None:
    """toggleDevMode checks innerWidth >= 768 before entering."""
    body = _extract_func(index_html, "toggleDevMode")
    assert "innerWidth < 768" in body


def test_toggle_narrow_viewport_toast(index_html: str) -> None:
    """toggleDevMode shows specific toast when viewport too narrow."""
    body = _extract_func(index_html, "toggleDevMode")
    assert "Dev Mode requires a wider viewport" in body


def test_showdevtab_persists_tab(index_html: str) -> None:
    """showDevTab writes active tab to localStorage."""
    body = _extract_func(index_html, "showDevTab")
    assert "localStorage.setItem('formforge-dev-tab'" in body


def test_boot_restores_active_tab(index_html: str) -> None:
    """Boot sequence restores last active dev tab."""
    assert "formforge-dev-tab" in index_html
    # The boot block should read the tab from localStorage
    assert "localStorage.getItem('formforge-dev-tab')" in index_html


# ============================================================
#  ISSUE #117 — Schema Builder with live form preview
# ============================================================


def test_schema_editor_debounce_300ms(index_html: str) -> None:
    """Schema editor uses 300ms debounce for preview updates."""
    body = _extract_func(index_html, "initSchemaEditor")
    assert "300" in body
    assert "devPreviewDebounce" in body or "setTimeout" in body


def test_schema_valid_badge_states(index_html: str) -> None:
    """devUpdateSchemaPreview sets badge to valid/invalid/parse error."""
    body = _extract_func(index_html, "devUpdateSchemaPreview")
    assert "'dev-validation-badge valid'" in body
    assert "'dev-validation-badge invalid'" in body
    assert "'parse error'" in body


def test_schema_errors_populated(index_html: str) -> None:
    """devUpdateSchemaPreview populates error panel with error details."""
    body = _extract_func(index_html, "devUpdateSchemaPreview")
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
    assert "Prism.highlight" in body
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
    assert "Prism.highlight" in body
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
    # Check the CSS rule
    match = re.search(r"\.dev-docx-preview\s*\{([^}]+)\}", index_html)
    assert match
    css = match.group(1)
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


def test_workspace_uses_show_directory_picker(index_html: str) -> None:
    """devOpenWorkspace calls showDirectoryPicker."""
    body = _extract_func(index_html, "devOpenWorkspace")
    assert "showDirectoryPicker" in body


def test_workspace_fsaa_feature_detect_hides_button(index_html: str) -> None:
    """Boot hides Open Folder button if FSAA not supported."""
    assert "!window.showDirectoryPicker" in index_html
    assert "btnOpenFolder" in index_html


def test_workspace_reads_schemas_and_templates(index_html: str) -> None:
    """devReadWorkspaceFromHandle reads schemas/ and templates/ dirs."""
    body = _extract_func(index_html, "devReadWorkspaceFromHandle")
    assert "'schemas'" in body or '"schemas"' in body
    assert "'templates'" in body or '"templates"' in body
    assert "_schema.spec.json" in body  # excluded
    assert "stencils.py" in body  # excluded


def test_workspace_excludes_stencils_in_drop_fallback(index_html: str) -> None:
    """Drag-and-drop fallback also excludes stencils.py from template listing."""
    body = _extract_func(index_html, "initWorkspaceDropZone")
    assert "stencils.py" in body


def test_workspace_renders_two_sections(index_html: str) -> None:
    """devRenderWorkspaceFiles renders Schemas and Templates sections."""
    body = _extract_func(index_html, "devRenderWorkspaceFiles")
    assert "Schemas" in body
    assert "Templates" in body
    assert "workspace-section" in body


def test_workspace_load_schema_switches_tab(index_html: str) -> None:
    """devLoadWorkspaceFile routes schema to dev-schema tab."""
    body = _extract_func(index_html, "devLoadWorkspaceFile")
    assert "showDevTab('dev-schema')" in body


def test_workspace_load_template_switches_tab(index_html: str) -> None:
    """devLoadWorkspaceFile routes template to dev-template tab."""
    body = _extract_func(index_html, "devLoadWorkspaceFile")
    assert "showDevTab('dev-template')" in body


def test_workspace_hover_action_text(index_html: str) -> None:
    """Workspace file items show action text on hover via CSS."""
    assert "workspace-file-action" in index_html
    # CSS: opacity 0 by default, 1 on hover
    match = re.search(r"\.workspace-file-action\s*\{[^}]*opacity:\s*0", index_html)
    assert match, "file-action should be opacity:0 by default"
    match2 = re.search(
        r"\.workspace-file-item:hover\s+\.workspace-file-action\s*\{[^}]*opacity:\s*1",
        index_html,
    )
    assert match2, "file-action should be opacity:1 on hover"


def test_workspace_badge_shows_file_count(index_html: str) -> None:
    """devReadWorkspaceFromHandle updates badge with file count."""
    body = _extract_func(index_html, "devReadWorkspaceFromHandle")
    assert "workspaceBadgeText" in body or "badgeText" in body
    assert "file" in body  # "N file(s) loaded"


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


def test_workspace_refresh_button_appears(index_html: str) -> None:
    """Refresh button is shown after folder is loaded."""
    assert 'id="btnRefreshWorkspace"' in index_html
    assert "btnRefreshWorkspace" in index_html
    body = _extract_func(index_html, "devReadWorkspaceFromHandle")
    assert "btnRefreshWorkspace" in body
    assert "'inline-flex'" in body


def test_workspace_dragdrop_uses_webkit_entry(index_html: str) -> None:
    """Drop handler uses webkitGetAsEntry as fallback."""
    body = _extract_func(index_html, "initWorkspaceDropZone")
    assert "webkitGetAsEntry" in body


def test_workspace_dragover_class(index_html: str) -> None:
    """Drop zone adds drag-over class on dragover."""
    body = _extract_func(index_html, "initWorkspaceDropZone")
    assert "'drag-over'" in body or '"drag-over"' in body


def test_workspace_drop_fsaa_fallthrough_warns(index_html: str) -> None:
    """FSAA drop error logs console.warn before falling through."""
    body = _extract_func(index_html, "initWorkspaceDropZone")
    assert "console.warn" in body


def test_workspace_drop_fsaa_handle_enables_polling(index_html: str) -> None:
    """If dropped item has FSAA handle, it is stored for polling."""
    body = _extract_func(index_html, "initWorkspaceDropZone")
    assert "workspaceHandle = handle" in body
    assert "devReadWorkspaceFromHandle()" in body


def test_workspace_drag_over_css(index_html: str) -> None:
    """CSS rule for .drag-over state on workspace drop zone."""
    match = re.search(r"\.workspace-drop-zone\.drag-over\s*\{([^}]+)\}", index_html)
    assert match
    css = match.group(1)
    assert "border-color" in css


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


def test_resize_handler_auto_exits(index_html: str) -> None:
    """handleDevModeResize exits dev mode when width drops below 768px."""
    body = _extract_func(index_html, "handleDevModeResize")
    assert "devMode = false" in body
    assert "innerWidth < 768" in body


def test_resize_handler_toast_message(index_html: str) -> None:
    """handleDevModeResize shows specific toast on auto-exit."""
    body = _extract_func(index_html, "handleDevModeResize")
    assert "Dev Mode disabled" in body
    assert "viewport too narrow" in body


def test_resize_handler_writes_localstorage(index_html: str) -> None:
    """handleDevModeResize sets localStorage to '0'."""
    body = _extract_func(index_html, "handleDevModeResize")
    assert "localStorage.setItem('formforge-dev-mode', '0')" in body


def test_resize_handler_returns_to_setup(index_html: str) -> None:
    """handleDevModeResize calls showView('setup')."""
    body = _extract_func(index_html, "handleDevModeResize")
    assert "showView('setup')" in body


def test_boot_width_guard(index_html: str) -> None:
    """Boot sequence only restores dev mode on viewports >= 768px."""
    # Find the DOMContentLoaded block
    match = re.search(r"DOMContentLoaded.*?\{([\s\S]*?)\}\);", index_html)
    assert match
    boot = match.group(1)
    assert "innerWidth >= 768" in boot
    assert "formforge-dev-mode" in boot


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

    def test_connect_repo_button_exists(self, index_html: str) -> None:
        """Connect Repo button exists in workspace toolbar."""
        assert 'id="btnConnectRepo"' in index_html

    def test_connect_repo_button_uses_github_icon(self, index_html: str) -> None:
        """Connect Repo button uses the GitHub icon."""
        match = re.search(r'id="btnConnectRepo"[^>]*>.*?</button>', index_html, re.S)
        assert match
        assert "#icon-github" in match.group(0)

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

    def test_branch_selector_exists(self, index_html: str) -> None:
        """Branch selector dropdown exists in workspace toolbar."""
        assert 'id="ghBranchSelect"' in index_html

    def test_new_branch_button_exists(self, index_html: str) -> None:
        """New branch button exists."""
        assert 'id="btnGhNewBranch"' in index_html

    def test_new_branch_input_exists(self, index_html: str) -> None:
        """New branch name input exists."""
        assert 'id="ghNewBranchName"' in index_html

    def test_commit_button_exists(self, index_html: str) -> None:
        """Commit button exists in workspace toolbar."""
        assert 'id="btnGhCommit"' in index_html

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

    def test_workspace_bar_hidden_by_default(self, index_html: str) -> None:
        """GitHub workspace bar is hidden by default."""
        match = re.search(r'id="ghWorkspaceBar"[^>]*>', index_html)
        assert match
        assert "display:none" in match.group(0)


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
            "gh-workspace-bar",
            "gh-branch-select",
            "gh-commit-panel",
            "gh-commit-file-list",
            "gh-commit-file-entry",
            "gh-commit-msg",
            "gh-commit-actions",
            "gh-new-branch-row",
            "workspace-file-name.modified",
        ],
    )
    def test_css_class_defined(self, index_html: str, css_class: str) -> None:
        """All GitHub workspace CSS classes are defined in the stylesheet."""
        assert f".{css_class}" in index_html


class TestGitHubWorkspaceJavaScript:
    """JavaScript function and pattern tests for GitHub workspace."""

    def test_state_variables_exist(self, index_html: str) -> None:
        """GitHub workspace state variables are declared."""
        assert "devGhConnected" in index_html
        assert "devGhOwner" in index_html
        assert "devGhRepoName" in index_html
        assert "devGhBranch" in index_html
        assert "devGhPat" in index_html
        assert "devGhBranches" in index_html
        assert "devGhOriginalContents" in index_html
        assert "devGhModifiedFiles" in index_html

    def test_token_localstorage_key(self, index_html: str) -> None:
        """Token uses the correct localStorage key."""
        assert "formforge-dev-github-token" in index_html

    def test_repo_localstorage_key(self, index_html: str) -> None:
        """Repo info uses the correct localStorage key."""
        assert "formforge-dev-github-repo" in index_html

    def test_token_stored_in_localstorage(self, index_html: str) -> None:
        """Token is stored to localStorage on connect."""
        assert "localStorage.setItem('formforge-dev-github-token'" in index_html

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
        assert "devGhOriginalContents" in body
        assert "devGhModifiedFiles" in body

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
        assert "devGhConnected = false" in body
        assert "devGhOwner = ''" in body
        assert "devGhModifiedFiles" in body

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
            r"function devGhHeaders\(\)([\s\S]*?)^(?:async )?function ",
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
