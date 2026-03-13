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
    """The mode toggle must be hidden on narrow viewports."""
    # Find the @media block for 768px in section 36
    pattern = (
        r"@media\s*\(max-width:\s*768px\)\s*\{[^}]*\.mode-toggle\s*\{\s*display:\s*none"
    )
    assert re.search(pattern, index_html), "mode-toggle must be display:none at <=768px"


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
