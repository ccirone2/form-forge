"""End-to-end browser tests for the context menu system.

Uses Playwright to exercise runtime behavior:
- Right-click in schema/template editors opens context menus
- Cursor-aware menu structure (flat items with group labels, no submenus)
- Snippet insertion into editors
- Menu close behavior (click-outside, Escape)
- Error handling (invalid JSON toast)
- Bounding element clamping (menu stays within editor pane)

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


def _activate_schema_tab(pg):
    """Navigate to the Schema tab and ensure the editor is ready.

    Clicks the Schema tab, which triggers ``loadDevModeDeps()`` to load
    CDN dependencies (Prism, CodeJar via dynamic import, mammoth, DOMPurify),
    then ``initSchemaEditor()`` initialises the CodeJar editor.
    """
    pg.click("#tab-dev-schema")

    # Wait for CDN deps to load and schema editor to initialise.
    # CodeJar sets contenteditable on the editor element.
    # Allow 30s for CDN loads which can be slow in CI environments.
    pg.wait_for_selector("#schemaEditor[contenteditable]", timeout=30000)


@pytest.fixture()
def page(browser_instance, server):
    """Create a new page, navigate to index.html, and open the Schema tab.

    Each test gets a fresh page so state does not leak between tests.
    """
    ctx = browser_instance.new_context(viewport={"width": 1280, "height": 900})
    pg = ctx.new_page()
    pg.goto(f"{server}/index.html", wait_until="networkidle")
    _activate_schema_tab(pg)
    yield pg
    ctx.close()


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------


def _dispatch_contextmenu(page, editor_id):
    """Dispatch a contextmenu event on the editor without moving the cursor.

    Playwright's ``click(button="right")`` repositions the text caret to the
    click coordinates, overriding any cursor position set by
    ``devSetCursorOffset``.  Dispatching the event via JS preserves the
    caret so that ``devGetCursorOffset`` returns the intended position.
    """
    page.evaluate(
        f"""(() => {{
            const el = document.getElementById('{editor_id}');
            const rect = el.getBoundingClientRect();
            el.dispatchEvent(new MouseEvent('contextmenu', {{
                bubbles: true, cancelable: true,
                clientX: rect.left + 10, clientY: rect.top + 10
            }}));
        }})()"""
    )


def open_schema_context_menu(page):
    """Right-click inside the schema editor and wait for the context menu."""
    _dispatch_contextmenu(page, "schemaEditor")
    page.wait_for_selector('#ctxMenu[style*="display: block"]', timeout=3000)
    return page.locator("#ctxMenu")


def open_template_context_menu(page, level="body"):
    """Switch to template tab, position cursor, and open context menu.

    Args:
        level: ``'body'`` (default) places cursor inside the function body so
               the menu shows stencil helpers.  ``'top'`` places cursor at the
               very start for top-level items.
    """
    page.click("#tab-dev-template")
    page.wait_for_selector("#templateEditor[contenteditable]", timeout=15000)
    # Position cursor so context detection gives the expected level
    if level == "body":
        page.evaluate(
            """(() => {
                const el = document.getElementById('templateEditor');
                el.focus();
                const text = devTemplateText || '';
                const defIdx = text.indexOf('def ');
                if (defIdx >= 0) {
                    const nl = text.indexOf('\\n', defIdx);
                    if (nl >= 0) {
                        devSetCursorOffset(el, nl + 5);
                        return;
                    }
                }
                devSetCursorOffset(el, Math.min(50, text.length));
            })()"""
        )
    else:
        page.evaluate(
            """(() => {
                const el = document.getElementById('templateEditor');
                el.focus();
                devSetCursorOffset(el, 0);
            })()"""
        )
    page.wait_for_timeout(100)
    _dispatch_contextmenu(page, "templateEditor")
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
    """Menu shows cursor-aware flat items with group labels (no submenus).

    The default starter schema has sections with fields, so right-clicking
    in the editor lands inside a section/field context. The menu should show
    flat field type items with category group labels.
    """

    def test_no_submenus(self, page):
        """Editor context menus are flat — no submenu items."""
        open_schema_context_menu(page)
        submenus = page.locator("#ctxMenu > .ctx-menu-item.has-sub")
        assert submenus.count() == 0

    def test_has_group_labels(self, page):
        """Section-level context shows group labels for field categories."""
        # Place cursor inside a section (click on "Section 1" text area)
        page.evaluate(
            """(() => {
                const text = devSchemaText;
                const sectionPos = text.indexOf('"fields"');
                if (sectionPos > 0) {
                    const el = document.getElementById('schemaEditor');
                    el.focus();
                    devSetCursorOffset(el, sectionPos + 10);
                }
            })()"""
        )
        page.wait_for_timeout(100)
        open_schema_context_menu(page)
        labels = page.locator("#ctxMenu > .ctx-menu-group-label")
        texts = [labels.nth(i).text_content().strip() for i in range(labels.count())]
        assert "Input Fields" in texts
        assert "Choice Fields" in texts

    def test_field_type_items_visible(self, page):
        """Section-level context shows flat field type items."""
        page.evaluate(
            """(() => {
                const text = devSchemaText;
                const pos = text.indexOf('"fields"');
                if (pos > 0) {
                    const el = document.getElementById('schemaEditor');
                    el.focus();
                    devSetCursorOffset(el, pos + 10);
                }
            })()"""
        )
        page.wait_for_timeout(100)
        open_schema_context_menu(page)
        items = page.locator("#ctxMenu > .ctx-menu-item")
        texts = [items.nth(i).text_content().strip() for i in range(items.count())]
        assert "Text" in texts
        assert "Select" in texts
        assert "Address" in texts

    def test_root_level_shows_structural_items(self, page):
        """When cursor is at root level, shows Add Section and Wrap in Wizard."""
        # Place cursor at the very start (root level)
        page.evaluate(
            """(() => {
                const el = document.getElementById('schemaEditor');
                el.focus();
                devSetCursorOffset(el, 1);
            })()"""
        )
        page.wait_for_timeout(100)
        open_schema_context_menu(page)
        items = page.locator("#ctxMenu > .ctx-menu-item")
        texts = [items.nth(i).text_content().strip() for i in range(items.count())]
        assert "Add Section" in texts
        assert "Wrap in Wizard" in texts


class TestSchemaSnippetInsertion:
    """Clicking a field type inserts a snippet into the schema JSON."""

    def test_insert_text_field(self, page):
        """Insert a Text field from the section-level context menu."""
        text_before = get_editor_text(page, "schemaEditor")
        # Position cursor inside the fields array of section
        page.evaluate(
            """(() => {
                const text = devSchemaText;
                const pos = text.indexOf('"fields"');
                if (pos > 0) {
                    const el = document.getElementById('schemaEditor');
                    el.focus();
                    devSetCursorOffset(el, pos + 10);
                }
            })()"""
        )
        page.wait_for_timeout(100)
        open_schema_context_menu(page)

        # Click "Text" item directly (no submenu hover needed)
        text_item = page.locator("#ctxMenu > .ctx-menu-item", has_text="Text").first
        text_item.click()

        # Menu should close
        assert not ctx_menu_visible(page)

        # Editor should now contain the inserted field
        text_after = get_editor_text(page, "schemaEditor")
        assert "text_field" in text_after
        assert len(text_after) > len(text_before)

    def test_insert_select_field(self, page):
        page.evaluate(
            """(() => {
                const text = devSchemaText;
                const pos = text.indexOf('"fields"');
                if (pos > 0) {
                    const el = document.getElementById('schemaEditor');
                    el.focus();
                    devSetCursorOffset(el, pos + 10);
                }
            })()"""
        )
        page.wait_for_timeout(100)
        open_schema_context_menu(page)
        select_item = page.locator(
            "#ctxMenu > .ctx-menu-item", has_text="Select"
        ).first
        select_item.click()
        text = get_editor_text(page, "schemaEditor")
        assert "select_field" in text

    def test_unique_id_on_duplicate(self, page):
        """Inserting the same field type twice gives unique IDs."""
        # Helper to position cursor and insert Text field
        def insert_text_field():
            page.evaluate(
                """(() => {
                    const text = devSchemaText;
                    const pos = text.indexOf('"fields"');
                    if (pos > 0) {
                        const el = document.getElementById('schemaEditor');
                        el.focus();
                        devSetCursorOffset(el, pos + 10);
                    }
                })()"""
            )
            page.wait_for_timeout(100)
            open_schema_context_menu(page)
            page.locator("#ctxMenu > .ctx-menu-item", has_text="Text").first.click()
            page.wait_for_timeout(100)

        insert_text_field()
        insert_text_field()
        text = get_editor_text(page, "schemaEditor")
        assert "text_field" in text
        assert "text_field_2" in text or "text_field_3" in text

    def test_add_section(self, page):
        # Place cursor at root level
        page.evaluate(
            """(() => {
                const el = document.getElementById('schemaEditor');
                el.focus();
                devSetCursorOffset(el, 1);
            })()"""
        )
        page.wait_for_timeout(100)
        open_schema_context_menu(page)
        page.locator(
            "#ctxMenu > .ctx-menu-item", has_text="Add Section"
        ).click()
        text = get_editor_text(page, "schemaEditor")
        assert "Section" in text

    def test_wrap_in_wizard(self, page):
        page.evaluate(
            """(() => {
                const el = document.getElementById('schemaEditor');
                el.focus();
                devSetCursorOffset(el, 1);
            })()"""
        )
        page.wait_for_timeout(100)
        open_schema_context_menu(page)
        page.locator(
            "#ctxMenu > .ctx-menu-item",
            has_text="Wrap in Wizard",
        ).click()
        text = get_editor_text(page, "schemaEditor")
        assert '"wizard"' in text or "wizard" in text


class TestSchemaFieldPropertyInsertion:
    """Field-level context shows property snippets for the detected type."""

    def test_field_level_shows_properties(self, page):
        """When cursor is inside a field object, shows property snippets."""
        # Position cursor inside the field_1 object (after "type": "text")
        page.evaluate(
            """(() => {
                const text = devSchemaText;
                const pos = text.indexOf('"type": "text"');
                if (pos > 0) {
                    const el = document.getElementById('schemaEditor');
                    el.focus();
                    devSetCursorOffset(el, pos + 5);
                }
            })()"""
        )
        page.wait_for_timeout(100)
        open_schema_context_menu(page)
        items = page.locator("#ctxMenu > .ctx-menu-item")
        texts = [items.nth(i).text_content().strip() for i in range(items.count())]
        # Text field should show common properties
        assert "placeholder" in texts
        assert "visible_when" in texts

    def test_insert_property(self, page):
        """Clicking a property snippet adds it to the field."""
        page.evaluate(
            """(() => {
                const text = devSchemaText;
                const pos = text.indexOf('"type": "text"');
                if (pos > 0) {
                    const el = document.getElementById('schemaEditor');
                    el.focus();
                    devSetCursorOffset(el, pos + 5);
                }
            })()"""
        )
        page.wait_for_timeout(100)
        open_schema_context_menu(page)
        page.locator("#ctxMenu > .ctx-menu-item", has_text="placeholder").click()
        page.wait_for_timeout(300)
        text = get_editor_text(page, "schemaEditor")
        assert "placeholder" in text


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
        # With invalid JSON, context detection falls back to root level
        items = page.locator("#ctxMenu > .ctx-menu-item")
        if items.count() > 0:
            items.first.click()

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
        page.evaluate(
            """(() => {
                const text = devSchemaText;
                const pos = text.indexOf('"fields"');
                if (pos > 0) {
                    const el = document.getElementById('schemaEditor');
                    el.focus();
                    devSetCursorOffset(el, pos + 10);
                }
            })()"""
        )
        page.wait_for_timeout(100)
        open_schema_context_menu(page)
        page.locator("#ctxMenu > .ctx-menu-item", has_text="Text").first.click()

        # Wait for preview debounce (300ms)
        page.wait_for_timeout(500)

        # Check the validation badge is visible
        badge = page.locator("#schemaValidBadge")
        assert badge.is_visible()

    def test_validation_badge_valid_after_insert(self, page):
        page.evaluate(
            """(() => {
                const text = devSchemaText;
                const pos = text.indexOf('"fields"');
                if (pos > 0) {
                    const el = document.getElementById('schemaEditor');
                    el.focus();
                    devSetCursorOffset(el, pos + 10);
                }
            })()"""
        )
        page.wait_for_timeout(100)
        open_schema_context_menu(page)
        page.locator("#ctxMenu > .ctx-menu-item", has_text="Email").first.click()

        page.wait_for_timeout(500)
        badge_text = page.locator("#schemaValidText").text_content()
        assert badge_text == "valid"


class TestSchemaMenuClamping:
    """Context menu stays within editor pane bounds."""

    def test_menu_within_editor_pane(self, page):
        """Menu position does not exceed the editor pane right/bottom edges."""
        open_schema_context_menu(page)
        result = page.evaluate(
            """(() => {
                const menu = document.getElementById('ctxMenu');
                const pane = document.getElementById('schemaEditorPane');
                const menuRect = menu.getBoundingClientRect();
                const paneRect = pane.getBoundingClientRect();
                return {
                    menuRight: menuRect.right,
                    menuBottom: menuRect.bottom,
                    paneRight: paneRect.right,
                    paneBottom: paneRect.bottom,
                };
            })()"""
        )
        # Menu should not exceed pane bounds (with small tolerance for rounding)
        assert result["menuRight"] <= result["paneRight"] + 2
        assert result["menuBottom"] <= result["paneBottom"] + 2


class TestBaseScaffold:
    """Base scaffold option appears when editor is empty."""

    def test_scaffold_shown_when_empty(self, page):
        """Clearing the editor and right-clicking shows Base Scaffold."""
        page.evaluate(
            """(() => {
                devSchemaText = '';
                if (window.schemaJar) schemaJar.updateCode('');
            })()"""
        )
        page.wait_for_timeout(200)
        # Position cursor at start
        page.evaluate(
            """(() => {
                const el = document.getElementById('schemaEditor');
                el.focus();
                devSetCursorOffset(el, 0);
            })()"""
        )
        page.wait_for_timeout(100)
        open_schema_context_menu(page)
        items = page.locator("#ctxMenu > .ctx-menu-item")
        texts = [items.nth(i).text_content().strip() for i in range(items.count())]
        assert "Base Scaffold" in texts

    def test_scaffold_inserts_valid_schema(self, page):
        """Clicking Base Scaffold inserts a complete valid schema."""
        page.evaluate(
            """(() => {
                devSchemaText = '';
                if (window.schemaJar) schemaJar.updateCode('');
            })()"""
        )
        page.wait_for_timeout(200)
        page.evaluate(
            """(() => {
                const el = document.getElementById('schemaEditor');
                el.focus();
                devSetCursorOffset(el, 0);
            })()"""
        )
        page.wait_for_timeout(100)
        open_schema_context_menu(page)
        page.locator("#ctxMenu > .ctx-menu-item", has_text="Base Scaffold").click()
        page.wait_for_timeout(500)
        text = get_editor_text(page, "schemaEditor")
        assert "New Form" in text
        assert "sections" in text
        assert "fields" in text


# ===========================================================================
#  Template Builder context menu tests
# ===========================================================================


class TestTemplateContextMenuAppears:
    """Right-click in the template editor opens the template context menu."""

    def test_right_click_opens_menu(self, page):
        menu = open_template_context_menu(page)
        assert menu.is_visible()


class TestTemplateMenuStructure:
    """Template menu has cursor-aware items — no submenus."""

    def test_no_submenus(self, page):
        """Template context menu has no submenu items."""
        open_template_context_menu(page)
        submenus = page.locator("#ctxMenu > .ctx-menu-item.has-sub")
        assert submenus.count() == 0

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


class TestTemplateMenuClamping:
    """Template context menu stays within editor pane bounds."""

    def test_menu_within_editor_pane(self, page):
        """Menu position does not exceed the template editor pane bounds."""
        open_template_context_menu(page)
        result = page.evaluate(
            """(() => {
                const menu = document.getElementById('ctxMenu');
                const pane = document.getElementById('templateEditorPane');
                const menuRect = menu.getBoundingClientRect();
                const paneRect = pane.getBoundingClientRect();
                return {
                    menuRight: menuRect.right,
                    menuBottom: menuRect.bottom,
                    paneRight: paneRect.right,
                    paneBottom: paneRect.bottom,
                };
            })()"""
        )
        assert result["menuRight"] <= result["paneRight"] + 2
        assert result["menuBottom"] <= result["paneBottom"] + 2
