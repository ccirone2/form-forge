"""
FormForge Shared Template Stencils
===================================
Shared helper functions for all FormForge DOCX templates.
Works in both standard Python (import stencils) and Pyodide (via exec()).

Usage in templates:
    import stencils
    doc = stencils.new_doc("My Form Title", "Subtitle here")
    stencils.table_section(doc, "Section Name", [("Label", "Value"), ...])
    stencils.longtext(doc, "Notes", some_text)
    stencils.bullet_list(doc, "Skills", newline_separated_str)
    stencils.signatures(doc, ["Signer 1", "Signer 2"])
    stencils.footer(doc)
    return stencils.finalize(doc)
"""

import io
import json
import base64
import binascii
from dataclasses import dataclass
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.image.exceptions import UnrecognizedImageError


# -- Palette system --

_PALETTE_ROLES = ("title", "subtitle", "muted", "footer", "accent")


@dataclass(frozen=True)
class Palette:
    """A set of semantic colors for DOCX document styling.

    Roles:
        title:    Main heading text color.
        subtitle: Subtitle text color.
        muted:    Empty-state / placeholder text color.
        footer:   Footer text color.
        accent:   Reserved for heavy emphasis / future use.
    """

    title: RGBColor
    subtitle: RGBColor
    muted: RGBColor
    footer: RGBColor
    accent: RGBColor


# Built-in palettes
PALETTE_CLASSIC = Palette(
    title=RGBColor(0x33, 0x33, 0x66),
    subtitle=RGBColor(0x66, 0x66, 0x99),
    muted=RGBColor(0x99, 0x99, 0x99),
    footer=RGBColor(0xAA, 0xAA, 0xAA),
    accent=RGBColor(0x1A, 0x1A, 0x3E),
)

PALETTE_MINIMAL = Palette(
    title=RGBColor(0x1A, 0x1A, 0x1A),
    subtitle=RGBColor(0x55, 0x55, 0x55),
    muted=RGBColor(0xAA, 0xAA, 0xAA),
    footer=RGBColor(0xCC, 0xCC, 0xCC),
    accent=RGBColor(0x00, 0x00, 0x00),
)

PALETTE_MODERN = Palette(
    title=RGBColor(0x1B, 0x5E, 0x6E),
    subtitle=RGBColor(0x4A, 0x8F, 0xA3),
    muted=RGBColor(0x8F, 0xA9, 0xB2),
    footer=RGBColor(0xB0, 0xC4, 0xCB),
    accent=RGBColor(0x0D, 0x3D, 0x4A),
)

_active_palette = PALETTE_CLASSIC


def set_palette(palette):
    """Set the active color palette for all subsequent stencils calls.

    Args:
        palette: A Palette instance (use a built-in PALETTE_* constant or
                 construct a custom Palette with all five role fields).

    Raises:
        ValueError: If palette is missing any required role field.
    """
    global _active_palette

    missing = [r for r in _PALETTE_ROLES if not hasattr(palette, r)]
    if missing:
        raise ValueError(f"Palette missing required roles: {', '.join(missing)}")

    _active_palette = palette


def new_doc(
    title_text, subtitle_text="", font_name="Calibri", font_size=11, palette=None
):
    """
    Create a styled Document with a centered title and optional subtitle.

    Args:
        title_text: Main heading text.
        subtitle_text: Optional subtitle displayed below the title.
        font_name: Base font for the document (default: "Calibri").
        font_size: Base font size in points (default: 11).
        palette: Optional Palette to use for title/subtitle colors.
                 If None, uses the current active palette.

    Returns:
        A python-docx Document instance.
    """
    p = palette if palette is not None else _active_palette
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = font_name
    style.font.size = Pt(font_size)

    title = doc.add_heading(title_text, level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in title.runs:
        run.font.color.rgb = p.title

    doc.add_paragraph("")

    if subtitle_text:
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run(subtitle_text)
        run.font.size = Pt(12)
        run.font.color.rgb = p.subtitle

        doc.add_paragraph("")

    return doc


def table_section(doc, heading, rows):
    """
    Add a heading followed by a two-column key/value table.

    Args:
        doc: The Document instance.
        heading: Section heading string.
        rows: List of (label, value) tuples.
    """
    doc.add_heading(heading, level=1)

    table = doc.add_table(rows=0, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Light Grid Accent 1"

    for label, value in rows:
        row = table.add_row()

        lp = row.cells[0].paragraphs[0]
        lr = lp.add_run(label)
        lr.bold = True
        lr.font.size = Pt(10)

        vp = row.cells[1].paragraphs[0]
        display_value = str(value) if value is not None and value != "" else "\u2014"
        vr = vp.add_run(display_value)
        vr.font.size = Pt(10)

    doc.add_paragraph("")


def longtext(doc, heading, text):
    """
    Add a sub-heading followed by one or more paragraphs of body text.
    Respects newline characters as paragraph breaks.

    Args:
        doc: The Document instance.
        heading: Sub-heading string.
        text: The long-form text content (may contain newlines).
    """
    doc.add_heading(heading, level=2)

    if text and text.strip():
        for paragraph_text in text.strip().split("\n"):
            if paragraph_text.strip():
                p = doc.add_paragraph()
                run = p.add_run(paragraph_text.strip())
                run.font.size = Pt(10)
    else:
        p = doc.add_paragraph()
        run = p.add_run("No information provided.")
        run.font.size = Pt(10)
        run.italic = True
        run.font.color.rgb = _active_palette.muted

    doc.add_paragraph("")


def bullet_list(doc, heading, items_str):
    """
    Add a sub-heading followed by a bulleted list.
    Items are expected as a newline-separated string.

    Args:
        doc: The Document instance.
        heading: Sub-heading string.
        items_str: Newline-separated string of list items.
    """
    doc.add_heading(heading, level=2)

    if items_str and items_str.strip():
        items = [item.strip() for item in items_str.split("\n") if item.strip()]
        for item in items:
            p = doc.add_paragraph(style="List Bullet")
            run = p.add_run(item)
            run.font.size = Pt(10)
    else:
        p = doc.add_paragraph()
        run = p.add_run("No items listed.")
        run.font.size = Pt(10)
        run.italic = True
        run.font.color.rgb = _active_palette.muted

    doc.add_paragraph("")


def signatures(doc, labels):
    """
    Add a signature block with underlines and labels in a grid layout.
    Labels are arranged in pairs (two per row).

    Args:
        doc: The Document instance.
        labels: List of signature label strings (e.g. ["Employee Signature",
                "Date", "HR Representative", "Date"]).
    """
    doc.add_paragraph("")
    doc.add_heading("Signatures", level=1)

    num_rows = (len(labels) + 1) // 2
    num_cols = min(len(labels), 2)
    sig_table = doc.add_table(rows=num_rows, cols=num_cols)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for i, label in enumerate(labels):
        cell = sig_table.rows[i // 2].cells[i % 2]
        p = cell.paragraphs[0]
        p.add_run("\n\n")
        p.add_run("_" * 35 + "\n")
        run = p.add_run(label)
        run.font.size = Pt(9)
        run.font.color.rgb = _active_palette.muted


def footer(doc):
    """
    Add the standard FormForge auto-generated footer paragraph.

    Args:
        doc: The Document instance.
    """
    doc.add_paragraph("")
    fp = doc.add_paragraph()
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = fp.add_run(
        "This document was auto-generated by FormForge. "
        "Please review all information for accuracy."
    )
    fr.font.size = Pt(8)
    fr.font.color.rgb = _active_palette.footer
    fr.italic = True


def address(doc, heading, raw_json):
    """
    Add a formatted mailing address block under a heading.
    Parses a JSON string with keys: street, city, state, zip.
    Handles empty/missing components gracefully.

    Args:
        doc: The Document instance.
        heading: Sub-heading string.
        raw_json: JSON string with address fields, or "{}".
    """
    doc.add_heading(heading, level=2)

    try:
        addr = json.loads(raw_json) if raw_json else {}
    except (json.JSONDecodeError, TypeError):
        addr = {}

    street = addr.get("street", "").strip()
    if street:
        p = doc.add_paragraph()
        r = p.add_run(street + "\n")
        r.font.size = Pt(10)

        # Build city/state/zip line, skipping empty parts
        parts = []
        city = addr.get("city", "").strip()
        state = addr.get("state", "").strip()
        zipcode = addr.get("zip", "").strip()
        if city:
            parts.append(city)
        if state:
            city_state = ", ".join(parts + [state]) if parts else state
            parts = [city_state]
        if zipcode:
            parts.append(zipcode)
        city_line = " ".join(parts)
        if city_line:
            r = p.add_run(city_line)
            r.font.size = Pt(10)
    else:
        p = doc.add_paragraph()
        r = p.add_run("No address provided.")
        r.italic = True
        r.font.color.rgb = _active_palette.muted

    doc.add_paragraph("")


def image(doc, b64_str, width_inches=3.0, placeholder="No image uploaded."):
    """
    Embed a base64 data-URI image or render a placeholder if absent/invalid.

    Args:
        doc: The Document instance.
        b64_str: Base64 data URI string (e.g. "data:image/png;base64,...") or "".
        width_inches: Image width in inches (default: 3.0).
        placeholder: Text to show when no image is available.
    """
    if b64_str and "," in b64_str:
        try:
            img_data = b64_str.split(",")[1]
            img_bytes = base64.b64decode(img_data)
            doc.add_picture(io.BytesIO(img_bytes), width=Inches(width_inches))
            return
        except (ValueError, binascii.Error, OSError, UnrecognizedImageError):
            pass

    p = doc.add_paragraph()
    r = p.add_run(placeholder)
    r.italic = True
    r.font.color.rgb = _active_palette.muted


def signature(doc, b64_str, label, width_inches=2.5):
    """
    Add a signature image (or placeholder underline) with a label beneath.

    Args:
        doc: The Document instance.
        b64_str: Base64 data URI string or "".
        label: Label text below the signature (e.g. "Employee Signature").
        width_inches: Signature image width in inches (default: 2.5).
    """
    p = doc.add_paragraph()
    if b64_str and "," in b64_str:
        try:
            sig_data = b64_str.split(",")[1]
            sig_bytes = base64.b64decode(sig_data)
            doc.add_picture(io.BytesIO(sig_bytes), width=Inches(width_inches))
        except (ValueError, binascii.Error, OSError, UnrecognizedImageError):
            p.add_run("_" * 40)
    else:
        p.add_run("_" * 40)
    lp = doc.add_paragraph()
    lr = lp.add_run(label)
    lr.font.size = Pt(9)
    lr.font.color.rgb = _active_palette.muted


def repeater_table(doc, headers, items, field_keys, currency_keys=None):
    """
    Render a repeater field as a headed table.

    Args:
        doc: The Document instance.
        headers: List of column header strings.
        items: List of dicts (parsed repeater JSON).
        field_keys: List of dict keys corresponding to each column.
        currency_keys: Optional set/list of field_keys that should be
                       formatted as currency (e.g. ["amount", "unit_cost"]).
    """
    if currency_keys is None:
        currency_keys = set()
    else:
        currency_keys = set(currency_keys)

    if items:
        table = doc.add_table(rows=1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Light Grid Accent 1"
        for i, header in enumerate(headers):
            cell_p = table.rows[0].cells[i].paragraphs[0]
            r = cell_p.add_run(header)
            r.bold = True
            r.font.size = Pt(10)
        for item in items:
            row = table.add_row()
            for col_idx, key in enumerate(field_keys):
                val = item.get(key, "")
                if key in currency_keys:
                    try:
                        val = f"${float(val):,.2f}"
                    except (ValueError, TypeError):
                        val = str(val)
                row.cells[col_idx].text = val
    else:
        p = doc.add_paragraph()
        r = p.add_run("No line items provided.")
        r.italic = True
        r.font.color.rgb = _active_palette.muted

    doc.add_paragraph("")


def finalize(doc):
    """
    Serialize a Document to bytes.

    Args:
        doc: The Document instance.

    Returns:
        bytes: The .docx file as raw bytes.
    """
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
