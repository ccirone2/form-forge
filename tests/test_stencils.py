"""Tests for templates/stencils.py shared utilities."""

import sys
from pathlib import Path

# Add templates/ to path so `import stencils` works
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "templates"))

import stencils


def test_new_doc_creates_document():
    doc = stencils.new_doc("Test Title")
    assert doc is not None
    # Verify the title heading exists
    assert len(doc.paragraphs) > 0


def test_new_doc_with_subtitle():
    doc = stencils.new_doc("Test Title", "Test Subtitle")
    texts = [p.text for p in doc.paragraphs]
    assert "Test Subtitle" in texts


def test_new_doc_default_font():
    doc = stencils.new_doc("Title")
    style = doc.styles["Normal"]
    assert style.font.name == "Segoe UI"
    assert style.font.size.pt == 11


def test_new_doc_custom_font():
    doc = stencils.new_doc("Title", font_name="Arial", font_size=12)
    style = doc.styles["Normal"]
    assert style.font.name == "Arial"
    assert style.font.size.pt == 12


def test_table_section():
    doc = stencils.new_doc("Test")
    stencils.table_section(
        doc,
        "Info",
        [
            ("Name", "Alice"),
            ("Role", "Developer"),
        ],
    )
    # Should have at least one table
    assert len(doc.tables) >= 1
    table = doc.tables[0]
    assert len(table.rows) == 2
    assert table.rows[0].cells[0].text == "Name"
    assert table.rows[0].cells[1].text == "Alice"


def test_table_section_empty_value():
    doc = stencils.new_doc("Test")
    stencils.table_section(
        doc,
        "Info",
        [
            ("Field", ""),
        ],
    )
    table = doc.tables[0]
    # Empty values should show em dash
    assert table.rows[0].cells[1].text == "\u2014"


def test_longtext_with_content():
    doc = stencils.new_doc("Test")
    stencils.longtext(doc, "Notes", "Line one\nLine two")
    texts = [p.text for p in doc.paragraphs]
    assert "Line one" in texts
    assert "Line two" in texts


def test_longtext_empty():
    doc = stencils.new_doc("Test")
    stencils.longtext(doc, "Notes", "")
    texts = [p.text for p in doc.paragraphs]
    assert "No information provided." in texts


def test_bullet_list_with_items():
    doc = stencils.new_doc("Test")
    stencils.bullet_list(doc, "Skills", "Python\nJavaScript\nRust")
    texts = [p.text for p in doc.paragraphs]
    assert "Python" in texts
    assert "JavaScript" in texts
    assert "Rust" in texts


def test_bullet_list_empty():
    doc = stencils.new_doc("Test")
    stencils.bullet_list(doc, "Skills", "")
    texts = [p.text for p in doc.paragraphs]
    assert "No items listed." in texts


def test_signatures():
    doc = stencils.new_doc("Test")
    stencils.signatures(doc, ["Employee", "Date", "Manager", "Date"])
    # Should create a table for signatures
    assert len(doc.tables) >= 1
    sig_table = doc.tables[-1]
    assert len(sig_table.rows) == 2
    assert len(sig_table.columns) == 2


def test_signatures_odd_count():
    doc = stencils.new_doc("Test")
    stencils.signatures(doc, ["Solo Signer"])
    sig_table = doc.tables[-1]
    assert len(sig_table.rows) == 1


def test_finalize_returns_valid_docx():
    doc = stencils.new_doc("Test")
    result = stencils.finalize(doc)
    assert isinstance(result, bytes)
    assert len(result) > 0
    # DOCX is a ZIP file — starts with PK
    assert result[:2] == b"PK"


# ── Palette tests (#48–#51) ─────────────────────────────────


def test_palette_classic_exists():
    p = stencils.PALETTE_CLASSIC
    assert p is not None
    assert hasattr(p, "title")
    assert hasattr(p, "subtitle")
    assert hasattr(p, "muted")
    assert hasattr(p, "footer")
    assert hasattr(p, "accent")


def test_palette_minimal_exists():
    p = stencils.PALETTE_MINIMAL
    assert p is not None
    assert hasattr(p, "title")
    assert hasattr(p, "subtitle")
    assert hasattr(p, "muted")
    assert hasattr(p, "footer")
    assert hasattr(p, "accent")


def test_palette_modern_exists():
    p = stencils.PALETTE_MODERN
    assert p is not None
    assert hasattr(p, "title")
    assert hasattr(p, "subtitle")
    assert hasattr(p, "muted")
    assert hasattr(p, "footer")
    assert hasattr(p, "accent")


def test_classic_palette_matches_legacy_constants():
    """PALETTE_CLASSIC roles must match the original COLOR_* values."""
    from docx.shared import RGBColor

    assert stencils.PALETTE_CLASSIC.title == RGBColor(0x33, 0x33, 0x66)
    assert stencils.PALETTE_CLASSIC.subtitle == RGBColor(0x66, 0x66, 0x99)
    assert stencils.PALETTE_CLASSIC.muted == RGBColor(0x99, 0x99, 0x99)
    assert stencils.PALETTE_CLASSIC.footer == RGBColor(0xAA, 0xAA, 0xAA)
    assert stencils.PALETTE_CLASSIC.accent == RGBColor(0x1A, 0x1A, 0x3E)


def test_set_palette_switches_title_color():
    try:
        stencils.set_palette(stencils.PALETTE_MINIMAL)
        doc = stencils.new_doc("Test")
        title_run = doc.paragraphs[0].runs[0]
        assert title_run.font.color.rgb == stencils.PALETTE_MINIMAL.title
    finally:
        stencils.set_palette(stencils.PALETTE_MODERN)


def test_set_palette_invalid_raises():
    import pytest

    with pytest.raises(ValueError, match="missing required roles"):
        stencils.set_palette(object())


def test_set_palette_custom_palette():
    from docx.shared import RGBColor

    custom = stencils.Palette(
        title=RGBColor(0xFF, 0x00, 0x00),
        subtitle=RGBColor(0x00, 0xFF, 0x00),
        muted=RGBColor(0x00, 0x00, 0xFF),
        footer=RGBColor(0xAA, 0xBB, 0xCC),
        accent=RGBColor(0x11, 0x22, 0x33),
    )
    try:
        stencils.set_palette(custom)
        doc = stencils.new_doc("Test")
        title_run = doc.paragraphs[0].runs[0]
        assert title_run.font.color.rgb == RGBColor(0xFF, 0x00, 0x00)
    finally:
        stencils.set_palette(stencils.PALETTE_MODERN)


def test_set_palette_restores_default():
    stencils.set_palette(stencils.PALETTE_MINIMAL)
    stencils.set_palette(stencils.PALETTE_MODERN)
    assert stencils._active_palette is stencils.PALETTE_MODERN


def test_new_doc_palette_override():
    """palette= on new_doc overrides title color without changing active palette."""
    before = stencils._active_palette
    doc = stencils.new_doc("Test", palette=stencils.PALETTE_MINIMAL)
    title_run = doc.paragraphs[0].runs[0]
    assert title_run.font.color.rgb == stencils.PALETTE_MINIMAL.title
    # Active palette unchanged
    assert stencils._active_palette is before


def test_new_doc_palette_override_does_not_change_active():
    before = stencils._active_palette
    stencils.new_doc("Test", palette=stencils.PALETTE_CLASSIC)
    assert stencils._active_palette is before


def test_new_doc_subtitle_palette_override():
    doc = stencils.new_doc("T", "Sub", palette=stencils.PALETTE_MODERN)
    # Subtitle is the 3rd paragraph (title, spacer, subtitle)
    subtitle_para = doc.paragraphs[2]
    assert subtitle_para.runs[0].font.color.rgb == stencils.PALETTE_MODERN.subtitle


def test_new_doc_no_palette_uses_active():
    try:
        stencils.set_palette(stencils.PALETTE_MINIMAL)
        doc = stencils.new_doc("Test")
        title_run = doc.paragraphs[0].runs[0]
        assert title_run.font.color.rgb == stencils.PALETTE_MINIMAL.title
    finally:
        stencils.set_palette(stencils.PALETTE_MODERN)


# ── Tests for table_section zero/falsy value fix ─────────────


def test_table_section_zero_value():
    doc = stencils.new_doc("Test")
    stencils.table_section(doc, "Info", [("Count", "0")])
    table = doc.tables[0]
    assert table.rows[0].cells[1].text == "0"


def test_table_section_numeric_zero():
    doc = stencils.new_doc("Test")
    stencils.table_section(doc, "Info", [("Count", 0)])
    table = doc.tables[0]
    assert table.rows[0].cells[1].text == "0"


# ── Tests for footer ─────────────────────────────────────────


def test_footer():
    doc = stencils.new_doc("Test")
    stencils.footer(doc)
    texts = [p.text for p in doc.paragraphs]
    assert any("auto-generated by FormForge" in t for t in texts)


# ── Tests for address ────────────────────────────────────────


def test_address_full():
    doc = stencils.new_doc("Test")
    import json

    addr = json.dumps(
        {"street": "123 Main St", "city": "Springfield", "state": "IL", "zip": "62701"}
    )
    stencils.address(doc, "Address", addr)
    texts = [p.text for p in doc.paragraphs]
    # Street should appear
    assert any("123 Main St" in t for t in texts)
    # City/state/zip should appear
    assert any("Springfield, IL 62701" in t for t in texts)


def test_address_empty_city():
    doc = stencils.new_doc("Test")
    import json

    addr = json.dumps(
        {"street": "123 Main St", "city": "", "state": "IL", "zip": "62701"}
    )
    stencils.address(doc, "Address", addr)
    texts = [p.text for p in doc.paragraphs]
    # Should NOT produce a leading comma
    for t in texts:
        assert not t.strip().startswith(",")


def test_address_no_street():
    doc = stencils.new_doc("Test")
    import json

    addr = json.dumps(
        {"street": "", "city": "Springfield", "state": "IL", "zip": "62701"}
    )
    stencils.address(doc, "Address", addr)
    texts = [p.text for p in doc.paragraphs]
    assert any("No address provided." in t for t in texts)


def test_address_empty_json():
    doc = stencils.new_doc("Test")
    stencils.address(doc, "Address", "{}")
    texts = [p.text for p in doc.paragraphs]
    assert any("No address provided." in t for t in texts)


# ── Tests for image ──────────────────────────────────────────


def test_image_empty():
    doc = stencils.new_doc("Test")
    stencils.image(doc, "", placeholder="No image.")
    texts = [p.text for p in doc.paragraphs]
    assert any("No image." in t for t in texts)


def test_image_invalid_b64():
    doc = stencils.new_doc("Test")
    stencils.image(doc, "data:image/png;base64,NOT_VALID!!!", placeholder="Failed.")
    texts = [p.text for p in doc.paragraphs]
    assert any("Failed." in t for t in texts)


# ── Tests for signature ──────────────────────────────────────


def test_signature_empty():
    doc = stencils.new_doc("Test")
    stencils.signature(doc, "", "Employee Signature")
    texts = [p.text for p in doc.paragraphs]
    assert any("Employee Signature" in t for t in texts)
    assert any("_" * 40 in t for t in texts)


def test_signature_invalid_b64():
    doc = stencils.new_doc("Test")
    stencils.signature(doc, "data:image/png;base64,BAD_DATA!!!", "Signer")
    texts = [p.text for p in doc.paragraphs]
    assert any("Signer" in t for t in texts)
    # Falls back to underline
    assert any("_" * 40 in t for t in texts)


# ── Tests for repeater_table ─────────────────────────────────


def test_repeater_table_with_items():
    doc = stencils.new_doc("Test")
    items = [
        {"desc": "Item A", "amount": "100.50"},
        {"desc": "Item B", "amount": "200"},
    ]
    stencils.repeater_table(
        doc,
        headers=["Description", "Amount"],
        items=items,
        field_keys=["desc", "amount"],
        currency_keys=["amount"],
    )
    assert len(doc.tables) >= 1
    table = doc.tables[0]
    # Header row + 2 data rows
    assert len(table.rows) == 3
    assert table.rows[1].cells[0].text == "Item A"
    assert table.rows[1].cells[1].text == "$100.50"
    assert table.rows[2].cells[1].text == "$200.00"


def test_repeater_table_empty():
    doc = stencils.new_doc("Test")
    stencils.repeater_table(
        doc,
        headers=["A", "B"],
        items=[],
        field_keys=["a", "b"],
    )
    texts = [p.text for p in doc.paragraphs]
    assert any("No line items provided." in t for t in texts)
