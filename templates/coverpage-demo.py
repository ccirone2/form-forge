"""
FormForge DOCX Template: Cover Page Demo
=========================================
Demonstrates the coverpage stencil — a professional title page with
company logo, document title/type, and metadata fields, followed by
body content on page 2.

The `data` dict keys match the field `id` values in
schemas/coverpage-demo.json.
"""

from stencils import Stencil, THEME_CLASSIC


def generate_docx(data: dict[str, str]) -> bytes:
    """
    Generate a document with a professional cover page.

    Args:
        data: dict mapping field IDs to their string values.

    Returns:
        bytes: The generated .docx file as raw bytes.
    """
    doc = Stencil()
    doc.set_theme(THEME_CLASSIC)
    doc.new_doc()

    # ── Cover page ──────────────────────────────────────────────
    doc.coverpage(
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
        doc.longtext(heading, data.get("body_content", ""))
    elif data.get("body_content", "").strip():
        doc.longtext("Content", data.get("body_content", ""))

    doc.bullet_list("Key Findings", data.get("key_findings", ""))

    # ── Footer ──────────────────────────────────────────────────
    doc.footer()

    return doc.finalize()
