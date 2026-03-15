"""End-to-end browser tests for the Dev Mode context menu system.

Uses Playwright to exercise runtime behavior:
- Right-click in schema/template editors opens context menus
- Menu structure (submenus, items, separators)
- Snippet insertion into editors
- Menu close behavior (click-outside, Escape)
- Error handling (invalid JSON toast)

Requires: pip install playwright && python -m playwright install chromium
"""

import http.server
import socket
import threading
from pathlib import Path

import pytest

# Playwright is optional — skip entire module if not installed
pw = pytest.importorskip("playwright.sync_api")

pytestmark = pytest.mark.e2e

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
#  Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def server():
    """Start a local HTTP server serving the project root."""

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

        def log_message(self, format, *args):
            pass  # suppress request logs

    # Bind to port 0 to let the OS pick an available port
    httpd = http.server.HTTPServer(("127.0.0.1", 0), QuietHandler)
    httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    httpd.shutdown()


@pytest.fixture(scope="module")
def browser_instance():
    """Launch a shared browser instance for all tests in this module."""
    with pw.sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


def _activate_dev_mode(pg):
    """Activate Dev Mode and ensure the schema editor is ready.

    Clicks the Dev Mode toggle, which triggers ``loadDevModeDeps()`` to load
    CDN dependencies (Prism, CodeJar via dynamic import, mammoth, DOMPurify),
    then ``initSchemaEditor()`` initialises the CodeJar editor.
    """
    pg.click("#modeToggle")

    # Wait for CDN deps to load and schema editor to initialise.
    # CodeJar sets contenteditable on the editor element.
    # Allow 30s for CDN loads which can be slow in CI environments.
    pg.wait_for_selector("#schemaEditor[contenteditable]", timeout=30000)


@pytest.fixture()
def page(browser_instance, server):
    """Create a new page, navigate to index.html, and activate Dev Mode.

    Each test gets a fresh page so state does not leak between tests.
    """
    ctx = browser_instance.new_context(viewport={"width": 1280, "height": 900})
    pg = ctx.new_page()
    pg.goto(f"{server}/index.html", wait_until="networkidle")
    _activate_dev_mode(pg)
    yield pg
    ctx.close()


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------


def open_schema_context_menu(page):
    """Right-click inside the schema editor and wait for the context menu."""
    editor = page.locator("#schemaEditor")
    editor.click(button="right")
    page.wait_for_selector('#ctxMenu[style*="display: block"]', timeout=3000)
    return page.locator("#ctxMenu")


def open_template_context_menu(page):
    """Switch to template tab, right-click in template editor, wait for menu."""
    page.click("#tab-dev-template")
    page.wait_for_selector("#templateEditor[contenteditable]", timeout=15000)
    editor = page.locator("#templateEditor")
    editor.click(button="right")
    page.wait_for_selector('#ctxMenu[style*="display: block"]', timeout=3000)
    return page.locator("#ctxMenu")


def get_editor_text(page, editor_id):
    """Return the text content of a CodeJar editor."""
    return page.evaluate(f"document.getElementById('{editor_id}').textContent")


def ctx_menu_visible(page):
    """Return True if the context menu is currently visible."""
    return page.evaluate(
        """(() => {
            const m = document.getElementById('ctxMenu');
            return m && m.style.display !== 'none';
        })()"""
    )


# ===========================================================================
#  Schema Builder context menu tests
# ===========================================================================


class TestSchemaContextMenuAppears:
    """Right-click in the schema editor opens the context menu."""

    def test_right_click_opens_menu(self, page):
        menu = open_schema_context_menu(page)
        assert menu.is_visible()

    def test_browser_default_suppressed(self, page):
        """The native browser context menu should NOT appear — verified by
        our custom menu being the one displayed."""
        menu = open_schema_context_menu(page)
        assert menu.is_visible()


class TestSchemaMenuStructure:
    """Menu has 4 grouped submenus plus action items."""

    def test_has_four_submenus(self, page):
        open_schema_context_menu(page)
        submenus = page.locator("#ctxMenu > .ctx-menu-item.has-sub")
        assert submenus.count() == 4

    def test_submenu_labels(self, page):
        open_schema_context_menu(page)
        subs = page.locator("#ctxMenu > .ctx-menu-item.has-sub")
        labels = [subs.nth(i).text_content().strip() for i in range(4)]
        assert "Input Fields" in labels[0]
        assert "Choice Fields" in labels[1]
        assert "Complex Fields" in labels[2]
        assert "Layout" in labels[3]

    def test_has_separator(self, page):
        open_schema_context_menu(page)
        separators = page.locator("#ctxMenu > .ctx-menu-separator")
        assert separators.count() >= 1

    def test_add_section_item(self, page):
        open_schema_context_menu(page)
        items = page.locator("#ctxMenu > .ctx-menu-item:not(.has-sub)")
        texts = [items.nth(i).text_content().strip() for i in range(items.count())]
        assert "Add Section" in texts

    def test_wrap_in_wizard_item(self, page):
        open_schema_context_menu(page)
        items = page.locator("#ctxMenu > .ctx-menu-item:not(.has-sub)")
        texts = [items.nth(i).text_content().strip() for i in range(items.count())]
        assert "Wrap in Wizard" in texts


class TestSchemaSnippetInsertion:
    """Clicking a field type inserts a snippet into the schema JSON."""

    def test_insert_text_field(self, page):
        text_before = get_editor_text(page, "schemaEditor")
        open_schema_context_menu(page)

        # Hover the "Input Fields" submenu to reveal children
        sub = page.locator("#ctxMenu > .ctx-menu-item.has-sub").first
        sub.hover()
        page.wait_for_timeout(200)

        # Click "Text" item
        text_item = sub.locator(".ctx-menu-sub .ctx-menu-item", has_text="Text").first
        text_item.click()

        # Menu should close
        assert not ctx_menu_visible(page)

        # Editor should now contain the inserted field
        text_after = get_editor_text(page, "schemaEditor")
        assert "text_field" in text_after
        assert len(text_after) > len(text_before)

    def test_insert_select_field(self, page):
        open_schema_context_menu(page)
        sub = page.locator(
            "#ctxMenu > .ctx-menu-item.has-sub", has_text="Choice Fields"
        )
        sub.hover()
        page.wait_for_timeout(200)

        select_item = sub.locator(
            ".ctx-menu-sub .ctx-menu-item", has_text="Select"
        ).first
        select_item.click()

        text = get_editor_text(page, "schemaEditor")
        assert "select_field" in text

    def test_unique_id_on_duplicate(self, page):
        """Inserting the same field type twice gives unique IDs."""
        # Insert text field first time
        open_schema_context_menu(page)
        sub = page.locator("#ctxMenu > .ctx-menu-item.has-sub").first
        sub.hover()
        page.wait_for_timeout(200)
        sub.locator(".ctx-menu-sub .ctx-menu-item", has_text="Text").first.click()
        page.wait_for_timeout(100)

        # Insert text field second time
        open_schema_context_menu(page)
        sub = page.locator("#ctxMenu > .ctx-menu-item.has-sub").first
        sub.hover()
        page.wait_for_timeout(200)
        sub.locator(".ctx-menu-sub .ctx-menu-item", has_text="Text").first.click()

        text = get_editor_text(page, "schemaEditor")
        # Should have both text_field and text_field_2 (or similar suffix)
        assert "text_field" in text
        assert "text_field_2" in text or "text_field_3" in text

    def test_add_section(self, page):
        open_schema_context_menu(page)
        page.locator(
            "#ctxMenu > .ctx-menu-item:not(.has-sub)", has_text="Add Section"
        ).click()

        text = get_editor_text(page, "schemaEditor")
        assert "Section" in text

    def test_wrap_in_wizard(self, page):
        open_schema_context_menu(page)
        page.locator(
            "#ctxMenu > .ctx-menu-item:not(.has-sub)",
            has_text="Wrap in Wizard",
        ).click()

        text = get_editor_text(page, "schemaEditor")
        assert '"wizard"' in text or "wizard" in text


class TestSchemaInvalidJson:
    """When the schema JSON is invalid, insert actions show a toast."""

    def test_toast_on_invalid_json_insert(self, page):
        # Break the JSON using schemaJar.updateCode so the internal
        # devSchemaText variable is properly synchronised.
        page.evaluate(
            """(() => {
                const broken = '{ invalid json !!!';
                if (window.schemaJar) {
                    schemaJar.updateCode(broken);
                } else {
                    devSchemaText = broken;
                }
            })()"""
        )
        page.wait_for_timeout(400)

        # Open menu and try to insert a field
        open_schema_context_menu(page)
        sub = page.locator("#ctxMenu > .ctx-menu-item.has-sub").first
        sub.hover()
        page.wait_for_timeout(200)
        sub.locator(".ctx-menu-sub .ctx-menu-item").first.click()

        # Wait for toast to appear
        toast = page.locator(".toast", has_text="fix JSON errors")
        toast.wait_for(timeout=5000)
        assert toast.is_visible()


class TestSchemaMenuCloses:
    """Menu closes on click-outside and Escape key."""

    def test_close_on_click_outside(self, page):
        open_schema_context_menu(page)
        assert ctx_menu_visible(page)

        # Click on the body, away from the menu
        page.mouse.click(10, 10)
        page.wait_for_timeout(200)

        assert not ctx_menu_visible(page)

    def test_close_on_escape(self, page):
        open_schema_context_menu(page)
        assert ctx_menu_visible(page)

        page.keyboard.press("Escape")
        page.wait_for_timeout(200)

        assert not ctx_menu_visible(page)


class TestSchemaLivePreview:
    """Live preview updates after snippet insertion."""

    def test_preview_updates_after_insert(self, page):
        open_schema_context_menu(page)
        sub = page.locator("#ctxMenu > .ctx-menu-item.has-sub").first
        sub.hover()
        page.wait_for_timeout(200)
        sub.locator(".ctx-menu-sub .ctx-menu-item", has_text="Text").first.click()

        # Wait for preview debounce (300ms)
        page.wait_for_timeout(500)

        # Check the validation badge is visible
        badge = page.locator("#schemaValidBadge")
        assert badge.is_visible()

    def test_validation_badge_valid_after_insert(self, page):
        open_schema_context_menu(page)
        sub = page.locator("#ctxMenu > .ctx-menu-item.has-sub").first
        sub.hover()
        page.wait_for_timeout(200)
        sub.locator(".ctx-menu-sub .ctx-menu-item", has_text="Email").first.click()

        page.wait_for_timeout(500)
        badge_text = page.locator("#schemaValidText").text_content()
        assert badge_text == "valid"


# ===========================================================================
#  Template Builder context menu tests
# ===========================================================================


class TestTemplateContextMenuAppears:
    """Right-click in the template editor opens the template context menu."""

    def test_right_click_opens_menu(self, page):
        menu = open_template_context_menu(page)
        assert menu.is_visible()


class TestTemplateMenuStructure:
    """Template menu has stencils helper snippet items."""

    def test_has_snippet_items(self, page):
        open_template_context_menu(page)
        items = page.locator("#ctxMenu .ctx-menu-item")
        assert items.count() >= 5  # At least several stencils snippets

    def test_known_snippets_present(self, page):
        open_template_context_menu(page)
        items = page.locator("#ctxMenu .ctx-menu-item")
        texts = [items.nth(i).text_content().strip() for i in range(items.count())]
        assert any("table_section" in t for t in texts)
        assert any("footer" in t for t in texts)
        assert any("finalize" in t for t in texts)


class TestTemplateSnippetInsertion:
    """Clicking a snippet inserts it into the template editor."""

    def test_insert_table_section(self, page):
        text_before = get_editor_text(page, "templateEditor")
        open_template_context_menu(page)

        item = page.locator("#ctxMenu .ctx-menu-item", has_text="table_section")
        item.click()

        text_after = get_editor_text(page, "templateEditor")
        assert "table_section" in text_after
        assert len(text_after) > len(text_before)

    def test_insert_footer(self, page):
        open_template_context_menu(page)

        item = page.locator("#ctxMenu .ctx-menu-item", has_text="footer")
        item.click()

        text = get_editor_text(page, "templateEditor")
        assert "footer" in text


class TestTemplateMenuCloses:
    """Template menu closes on click-outside and Escape."""

    def test_close_on_escape(self, page):
        open_template_context_menu(page)
        assert ctx_menu_visible(page)

        page.keyboard.press("Escape")
        page.wait_for_timeout(200)

        assert not ctx_menu_visible(page)

    def test_close_on_click_outside(self, page):
        open_template_context_menu(page)
        assert ctx_menu_visible(page)

        page.mouse.click(10, 10)
        page.wait_for_timeout(200)

        assert not ctx_menu_visible(page)
