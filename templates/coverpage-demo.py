"""
FormForge DOCX Template: Cover Page Demo
=========================================
Demonstrates the coverpage stencil — a professional title page with
company logo, document title/type, and metadata fields, followed by
body content on page 2.

The `data` dict keys match the field `id` values in
schemas/coverpage-demo.json.
"""

import stencils


def generate_docx(data: dict[str, str]) -> bytes:
    """
    Generate a document with a professional cover page.

    Args:
        data: dict mapping field IDs to their string values.

    Returns:
        bytes: The generated .docx file as raw bytes.
    """
    stencils.set_theme(stencils.THEME_CLASSIC)

    # Empty title — the cover page replaces the default heading
    doc = stencils.new_doc("", "")

    # ── Cover page ──────────────────────────────────────────────
    stencils.coverpage(
        doc,
        title=data.get("doc_title", "Untitled Document"),
        doc_type=data.get("doc_type", ""),
        metadata=[
            ("Date", data.get("doc_date", "")),
            ("Revision", data.get("revision", "")),
            ("Document ID", data.get("doc_id", "")),
            ("Author", data.get("author", "")),
        ],
        logo_b64=data.get("company_logo", ""),
    )

    # ── Body content (page 2+) ──────────────────────────────────
    heading = data.get("body_heading", "").strip()
    if heading:
        stencils.longtext(doc, heading, data.get("body_content", ""))
    elif data.get("body_content", "").strip():
        stencils.longtext(doc, "Content", data.get("body_content", ""))

    stencils.bullet_list(doc, "Key Findings", data.get("key_findings", ""))

    # ── Footer ──────────────────────────────────────────────────
    stencils.footer(doc)

    return stencils.finalize(doc)
