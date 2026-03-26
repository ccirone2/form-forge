"""Deterministic responsive screenshot capture for FormForge diagnostics.

Launches a local HTTP server, opens the app in headless Chromium via Playwright,
and captures every major screen at each responsive breakpoint. Output goes to
``screenshots/`` with filenames like ``01-forms-landing_1440x900.png``.

Usage::

    python scripts/take_screenshots.py          # all viewports
    python scripts/take_screenshots.py desktop   # single viewport by name
    python scripts/take_screenshots.py 1024x768  # single viewport by size

Requires: pip install playwright && python -m playwright install chromium
"""

import http.server
import os
import shutil
import socket
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "screenshots"

# Viewport breakpoints derived from the app's @media queries.
VIEWPORTS = [
    ("desktop", 1440, 900),
    ("laptop", 1024, 768),
    ("tablet", 768, 1024),
    ("mobile", 600, 900),
    ("mobile-sm", 400, 800),
]


# ---------------------------------------------------------------------------
#  Browser resolution
# ---------------------------------------------------------------------------


def _find_chromium():
    """Find a usable Chromium binary, returning its path or None.

    Checks (in order):
    1. CHROMIUM_PATH env var (explicit override)
    2. Playwright's cached ms-playwright builds (any version)
    3. System chromium/google-chrome on PATH
    Falls back to None, letting Playwright try its default.
    """
    # 1. Explicit override
    env_path = os.environ.get("CHROMIUM_PATH")
    if env_path and Path(env_path).is_file():
        return env_path

    # 2. Cached ms-playwright builds (glob for any chromium-* version)
    cache_dir = Path.home() / ".cache" / "ms-playwright"
    if cache_dir.is_dir():
        candidates = sorted(cache_dir.glob("chromium-*/chrome-linux/chrome"), reverse=True)
        for c in candidates:
            if c.is_file():
                return str(c)

    # 3. System browser
    for name in ("chromium", "google-chrome-stable", "google-chrome"):
        path = shutil.which(name)
        if path:
            return path

    return None


# ---------------------------------------------------------------------------
#  HTTP server (same pattern as tests/test_context_menu.py)
# ---------------------------------------------------------------------------


def _start_server():
    """Start a local HTTP server serving the project root. Returns base URL."""

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(PROJECT_ROOT), **kw)

        def log_message(self, format, *args):  # noqa: A002
            pass

    httpd = http.server.HTTPServer(("127.0.0.1", 0), QuietHandler)
    httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return f"http://127.0.0.1:{port}", httpd


# ---------------------------------------------------------------------------
#  Screen capture definitions
# ---------------------------------------------------------------------------


def _capture_forms_landing(page, out, label):
    """01 — Forms tab landing page (hero + source cards)."""
    page.screenshot(path=str(out / f"01-forms-landing_{label}.png"))


def _capture_connect_github(page, out, label):
    """02 — Connect dialog, GitHub tab."""
    page.evaluate("showConnectDialog()")
    page.wait_for_selector("#connectDialogOverlay.visible", timeout=5000)
    page.evaluate("switchConnectTab('github')")
    page.wait_for_timeout(300)
    page.screenshot(path=str(out / f"02-connect-github_{label}.png"))


def _capture_connect_local(page, out, label):
    """03 — Connect dialog, Local tab."""
    page.evaluate("switchConnectTab('local')")
    page.wait_for_timeout(300)
    page.screenshot(path=str(out / f"03-connect-local_{label}.png"))
    page.evaluate("hideConnectDialog()")
    page.wait_for_timeout(200)


def _capture_form_filled(page, out, label):
    """04 — Demo form filled with sample data."""
    # Launch the demo form without Pyodide (we only need the UI for screenshots).
    page.evaluate("""(() => {
        contentSourceType = 'demo';
        currentSchema = DEMO_SCHEMA;
        currentSchemaName = '';
        currentTemplateCode = DEMO_TEMPLATE;
        buildForm(currentSchema);
        showView('form');
    })()""")
    page.wait_for_selector("#view-form", state="visible", timeout=15000)
    page.wait_for_timeout(500)
    # Fill with the embedded sample data
    page.evaluate(
        "populateForm(currentSchema.sampleData, { skipFileFields: true })"
    )
    page.wait_for_timeout(500)
    page.screenshot(path=str(out / f"04-form-filled_{label}.png"))


def _capture_schema_editor(page, out, label):
    """05 — Schema tab with demo schema loaded in editor."""
    # showTab() requires CDN deps (Prism, CodeJar) which may be blocked.
    # Use showView() directly to switch the visible panel, and populate
    # the raw editor textarea with demo content as a fallback.
    # Clear formDirty so showView won't prompt a confirm dialog.
    page.evaluate("""(() => {
        formDirty = false;
        // Update tab bar visuals
        document.querySelectorAll('.dev-nav-tab').forEach(t => {
            t.classList.remove('active');
            t.setAttribute('aria-selected', 'false');
        });
        document.querySelectorAll('.dev-nav-tab[data-tab="dev-schema"]').forEach(t => {
            t.classList.add('active');
            t.setAttribute('aria-selected', 'true');
        });
        showView('dev-schema');
        // Populate editor with demo schema text if CodeJar isn't loaded
        const ed = document.getElementById('schemaEditor');
        if (ed && typeof DEMO_SCHEMA_JSON !== 'undefined') {
            ed.textContent = DEMO_SCHEMA_JSON;
        }
    })()""")
    page.wait_for_selector("#view-dev-schema.active", timeout=10000)
    page.wait_for_timeout(500)
    page.screenshot(path=str(out / f"05-schema-editor_{label}.png"))


def _capture_template_editor(page, out, label):
    """06 — Template tab with demo template loaded in editor."""
    page.evaluate("""(() => {
        document.querySelectorAll('.dev-nav-tab').forEach(t => {
            t.classList.remove('active');
            t.setAttribute('aria-selected', 'false');
        });
        document.querySelectorAll('.dev-nav-tab[data-tab="dev-template"]').forEach(t => {
            t.classList.add('active');
            t.setAttribute('aria-selected', 'true');
        });
        showView('dev-template');
        const ed = document.getElementById('templateEditor');
        if (ed && !ed.getAttribute('contenteditable') && typeof DEMO_TEMPLATE !== 'undefined') {
            ed.textContent = DEMO_TEMPLATE;
        }
    })()""")
    page.wait_for_selector("#view-dev-template", state="visible", timeout=10000)
    page.wait_for_timeout(500)
    page.screenshot(path=str(out / f"06-template-editor_{label}.png"))


def _capture_docs(page, out, label):
    """07 — Docs tab, Schema Guide sub-tab."""
    page.evaluate("""(() => {
        document.querySelectorAll('.dev-nav-tab').forEach(t => {
            t.classList.remove('active');
            t.setAttribute('aria-selected', 'false');
        });
        document.querySelectorAll('.dev-nav-tab[data-tab="dev-docs"]').forEach(t => {
            t.classList.add('active');
            t.setAttribute('aria-selected', 'true');
        });
        showView('dev-docs');
    })()""")
    page.wait_for_selector("#view-dev-docs", state="visible", timeout=10000)
    page.wait_for_timeout(500)
    page.screenshot(path=str(out / f"07-docs_{label}.png"))


# Ordered sequence — each step builds on the previous page state.
SCREENS = [
    _capture_forms_landing,
    _capture_connect_github,
    _capture_connect_local,
    _capture_form_filled,
    _capture_schema_editor,
    _capture_template_editor,
    _capture_docs,
]


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------


def _parse_filter():
    """Return a list of (name, w, h) tuples to capture, based on CLI args."""
    if len(sys.argv) < 2:
        return VIEWPORTS

    arg = sys.argv[1].lower()

    # Match by name
    for v in VIEWPORTS:
        if v[0] == arg:
            return [v]

    # Match by WxH
    if "x" in arg:
        parts = arg.split("x")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            w, h = int(parts[0]), int(parts[1])
            for v in VIEWPORTS:
                if v[1] == w and v[2] == h:
                    return [v]
            # Custom size
            return [(f"{w}x{h}", w, h)]

    print(f"Unknown viewport filter: {arg}")
    print("Available: " + ", ".join(f"{v[0]} ({v[1]}x{v[2]})" for v in VIEWPORTS))
    sys.exit(1)


def run():
    viewports = _parse_filter()

    OUTPUT_DIR.mkdir(exist_ok=True)

    base_url, httpd = _start_server()
    print(f"Server started at {base_url}")

    total = len(viewports) * len(SCREENS)
    count = 0

    with sync_playwright() as pw:
        # Resolve a usable Chromium binary: Playwright's bundled browser,
        # a system install, or a cached ms-playwright build.
        launch_opts = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-gpu"],
        }
        chromium_path = _find_chromium()
        if chromium_path:
            launch_opts["executable_path"] = chromium_path
        browser = pw.chromium.launch(**launch_opts)

        for vp_name, width, height in viewports:
            label = f"{width}x{height}"
            print(f"\n── {vp_name} ({label}) ──")

            ctx = browser.new_context(viewport={"width": width, "height": height})
            page = ctx.new_page()

            # Block all external requests (fonts, CDNs) that may hang in
            # sandboxed/offline environments. Playwright's screenshot waits
            # for document.fonts.ready which never resolves if font requests
            # are pending. The app renders fine with fallback system fonts.
            def _route_handler(route):
                if base_url in route.request.url:
                    route.continue_()
                else:
                    route.abort()

            page.route("**/*", _route_handler)

            page.goto(f"{base_url}/index.html", wait_until="commit", timeout=60000)
            # Wait for the app to initialise
            page.wait_for_selector("#view-setup", timeout=30000)
            # Clean up external refs so document.fonts.ready resolves
            page.evaluate("""
                document.querySelectorAll('link[href^="http"]').forEach(el => el.remove());
                document.querySelectorAll('script[src^="http"]').forEach(el => el.remove());
            """)
            page.wait_for_timeout(500)

            for capture_fn in SCREENS:
                capture_fn(page, OUTPUT_DIR, label)
                count += 1
                fname = capture_fn.__doc__.split("—")[0].strip() if capture_fn.__doc__ else capture_fn.__name__
                print(f"  [{count}/{total}] {fname}")

            ctx.close()

        browser.close()

    httpd.shutdown()

    print(f"\nDone — {count} screenshots saved to {OUTPUT_DIR.relative_to(PROJECT_ROOT)}/")


if __name__ == "__main__":
    run()
