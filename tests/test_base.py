"""Tests for templates/_base.py shared utilities."""

import sys
from pathlib import Path

# Add templates/ to path so `import _base` works
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "templates"))

import _base


def test_new_doc_creates_document():
    doc = _base.new_doc("Test Title")
    assert doc is not None
    # Verify the title heading exists
    assert len(doc.paragraphs) > 0


def test_new_doc_with_subtitle():
    doc = _base.new_doc("Test Title", "Test Subtitle")
    texts = [p.text for p in doc.paragraphs]
    assert "Test Subtitle" in texts


def test_new_doc_default_font():
    doc = _base.new_doc("Title")
    style = doc.styles["Normal"]
    assert style.font.name == "Calibri"
    assert style.font.size.pt == 11


def test_new_doc_custom_font():
    doc = _base.new_doc("Title", font_name="Arial", font_size=12)
    style = doc.styles["Normal"]
    assert style.font.name == "Arial"
    assert style.font.size.pt == 12


def test_add_table_section():
    doc = _base.new_doc("Test")
    _base.add_table_section(doc, "Info", [
        ("Name", "Alice"),
        ("Role", "Developer"),
    ])
    # Should have at least one table
    assert len(doc.tables) >= 1
    table = doc.tables[0]
    assert len(table.rows) == 2
    assert table.rows[0].cells[0].text == "Name"
    assert table.rows[0].cells[1].text == "Alice"


def test_add_table_section_empty_value():
    doc = _base.new_doc("Test")
    _base.add_table_section(doc, "Info", [
        ("Field", ""),
    ])
    table = doc.tables[0]
    # Empty values should show em dash
    assert table.rows[0].cells[1].text == "\u2014"


def test_add_longtext_with_content():
    doc = _base.new_doc("Test")
    _base.add_longtext(doc, "Notes", "Line one\nLine two")
    texts = [p.text for p in doc.paragraphs]
    assert "Line one" in texts
    assert "Line two" in texts


def test_add_longtext_empty():
    doc = _base.new_doc("Test")
    _base.add_longtext(doc, "Notes", "")
    texts = [p.text for p in doc.paragraphs]
    assert "No information provided." in texts


def test_add_bullet_list_with_items():
    doc = _base.new_doc("Test")
    _base.add_bullet_list(doc, "Skills", "Python\nJavaScript\nRust")
    texts = [p.text for p in doc.paragraphs]
    assert "Python" in texts
    assert "JavaScript" in texts
    assert "Rust" in texts


def test_add_bullet_list_empty():
    doc = _base.new_doc("Test")
    _base.add_bullet_list(doc, "Skills", "")
    texts = [p.text for p in doc.paragraphs]
    assert "No items listed." in texts


def test_add_signatures():
    doc = _base.new_doc("Test")
    _base.add_signatures(doc, ["Employee", "Date", "Manager", "Date"])
    # Should create a table for signatures
    assert len(doc.tables) >= 1
    sig_table = doc.tables[-1]
    assert len(sig_table.rows) == 2
    assert len(sig_table.columns) == 2


def test_add_signatures_odd_count():
    doc = _base.new_doc("Test")
    _base.add_signatures(doc, ["Solo Signer"])
    sig_table = doc.tables[-1]
    assert len(sig_table.rows) == 1


def test_finalize_returns_valid_docx():
    doc = _base.new_doc("Test")
    result = _base.finalize(doc)
    assert isinstance(result, bytes)
    assert len(result) > 0
    # DOCX is a ZIP file — starts with PK
    assert result[:2] == b"PK"


def test_color_constants_exist():
    assert _base.COLOR_DARK_NAVY is not None
    assert _base.COLOR_MEDIUM_BLUE is not None
    assert _base.COLOR_SOFT_BLUE is not None
    assert _base.COLOR_MUTED is not None
    assert _base.COLOR_LIGHT_MUTED is not None
