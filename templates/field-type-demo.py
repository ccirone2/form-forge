"""
FormForge DOCX Template: Event Registration (Field Type Demo)
=============================================================
Demonstrates all 17 field types, wizard mode, and conditional visibility.

Field type value formats:
  - text/email/tel/date/select/radio/textarea → str
  - number/currency → str (e.g. "50", "1250.00")
  - hidden → str (static default_value from schema)
  - heading → not passed (skipped in collectFormData)
  - checkbox → comma-separated str
  - longtext → str with possible newlines
  - list → newline-separated str
  - address → JSON string: {"street","city","state","zip"}
  - file/signature → base64 data URI str or ""
  - repeater → JSON array string: [{"field":"value"}, ...]
"""

import io
import json
import base64
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

import _base


def generate_docx(data):
    """
    Generate an Event Registration document from form data.

    Args:
        data: dict mapping field IDs to their string values.

    Returns:
        bytes: The generated .docx file as raw bytes.
    """
    name = data.get("full_name", "")
    email = data.get("email", "")
    event_date = data.get("event_date", "")
    form_ver = data.get("form_version", "")

    doc = _base.new_doc(
        "Event Registration",
        f"{name} — {event_date}",
    )

    # ── Step 1: Applicant Info ────────────────────────────
    _base.add_table_section(
        doc,
        "Applicant Info",
        [
            ("Full Name", name),
            ("Email", email),
            ("Phone", data.get("phone", "")),
            ("Preferred Date", event_date),
            ("Form Version", form_ver),
        ],
    )

    # ── Step 2: Event Details ─────────────────────────────
    event_type = data.get("event_type", "")
    attendance = data.get("attendance_mode", "")

    _base.add_table_section(
        doc,
        "Event Details",
        [
            ("Event Type", event_type),
            ("Attendance Mode", attendance),
        ],
    )

    # textarea — brief description
    description = data.get("event_description", "")
    if description and description.strip():
        doc.add_heading("Brief Description", level=2)
        p = doc.add_paragraph()
        r = p.add_run(description)
        r.font.size = Pt(10)
        doc.add_paragraph("")

    # longtext — detailed proposal
    proposal = data.get("detailed_proposal", "")
    if proposal and proposal.strip():
        _base.add_longtext(doc, "Detailed Proposal", proposal)

    # address (conditional — in-person only)
    raw_addr = data.get("venue_address", "{}")
    try:
        addr = json.loads(raw_addr)
    except (json.JSONDecodeError, TypeError):
        addr = {}

    if addr.get("street"):
        doc.add_heading("Venue Address", level=2)
        p = doc.add_paragraph()
        lines = [
            addr.get("street", ""),
            f"{addr.get('city', '')}, {addr.get('state', '')} {addr.get('zip', '')}".strip(),
        ]
        for line in lines:
            if line.strip() and line.strip() != ",":
                r = p.add_run(line.strip() + "\n")
                r.font.size = Pt(10)
        doc.add_paragraph("")

    # checkbox (conditional — in-person dietary restrictions)
    dietary = data.get("dietary_restrictions", "")
    if dietary and dietary.strip():
        doc.add_heading("Dietary Restrictions", level=2)
        for item in dietary.split(","):
            item = item.strip()
            if item:
                p = doc.add_paragraph(style="List Bullet")
                r = p.add_run(item)
                r.font.size = Pt(10)
        doc.add_paragraph("")

    # text (conditional — virtual platform)
    virtual_platform = data.get("virtual_platform", "")
    if virtual_platform and virtual_platform.strip():
        doc.add_heading("Virtual Platform", level=2)
        p = doc.add_paragraph()
        r = p.add_run(virtual_platform)
        r.font.size = Pt(10)
        doc.add_paragraph("")

    # ── Step 3: Budget & Items ────────────────────────────
    budget = data.get("budget_amount", "0")
    try:
        budget_fmt = f"${float(budget):,.2f}"
    except (ValueError, TypeError):
        budget_fmt = f"${budget}"

    attendees = data.get("attendee_count", "")

    _base.add_table_section(
        doc,
        "Budget & Logistics",
        [
            ("Estimated Budget", budget_fmt),
            ("Expected Attendees", attendees),
        ],
    )

    # repeater — expense line items
    doc.add_heading("Budget Line Items", level=1)
    raw_items = data.get("expense_items", "[]")
    try:
        items = json.loads(raw_items)
    except (json.JSONDecodeError, TypeError):
        items = []

    if items:
        table = doc.add_table(rows=1, cols=4)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Light Grid Accent 1"
        for i, header in enumerate(["Item", "Qty", "Unit Cost", "Category"]):
            cell_p = table.rows[0].cells[i].paragraphs[0]
            r = cell_p.add_run(header)
            r.bold = True
            r.font.size = Pt(10)
        for item in items:
            row = table.add_row()
            row.cells[0].text = item.get("item_name", "")
            row.cells[1].text = item.get("quantity", "")
            cost = item.get("unit_cost", "0")
            try:
                row.cells[2].text = f"${float(cost):,.2f}"
            except (ValueError, TypeError):
                row.cells[2].text = str(cost)
            row.cells[3].text = item.get("category", "")
    else:
        p = doc.add_paragraph()
        r = p.add_run("No line items provided.")
        r.italic = True
        r.font.color.rgb = _base.COLOR_MUTED

    doc.add_paragraph("")

    # list — special requests
    special = data.get("special_requests", "")
    if special and special.strip():
        _base.add_bullet_list(doc, "Special Requests", special)

    # ── Step 4: Attachments & Approval ────────────────────

    # file — supporting document
    doc.add_heading("Supporting Document", level=1)
    doc_b64 = data.get("supporting_doc", "")
    if doc_b64 and "," in doc_b64:
        try:
            img_data = doc_b64.split(",")[1]
            img_bytes = base64.b64decode(img_data)
            doc.add_picture(io.BytesIO(img_bytes), width=Inches(3))
        except Exception:
            p = doc.add_paragraph()
            r = p.add_run("[Document could not be embedded]")
            r.italic = True
            r.font.color.rgb = _base.COLOR_MUTED
    else:
        p = doc.add_paragraph()
        r = p.add_run("No document uploaded.")
        r.italic = True
        r.font.color.rgb = _base.COLOR_MUTED

    doc.add_paragraph("")

    # textarea — additional notes
    notes = data.get("additional_notes", "")
    if notes and notes.strip():
        doc.add_heading("Additional Notes", level=1)
        p = doc.add_paragraph()
        r = p.add_run(notes)
        r.font.size = Pt(10)
        doc.add_paragraph("")

    # signature — applicant signature
    doc.add_heading("Applicant Signature", level=1)
    sig_b64 = data.get("applicant_signature", "")
    if sig_b64 and "," in sig_b64:
        try:
            sig_data = sig_b64.split(",")[1]
            sig_bytes = base64.b64decode(sig_data)
            doc.add_picture(io.BytesIO(sig_bytes), width=Inches(2.5))
        except Exception:
            p = doc.add_paragraph()
            r = p.add_run("_" * 40)
    else:
        p = doc.add_paragraph()
        r = p.add_run("_" * 40)
    lp = doc.add_paragraph()
    lr = lp.add_run("Applicant Signature")
    lr.font.size = Pt(9)
    lr.font.color.rgb = _base.COLOR_MUTED

    doc.add_paragraph("")

    # ── Footer ────────────────────────────────────────────
    fp = doc.add_paragraph()
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = fp.add_run(
        "This document was auto-generated by FormForge. "
        "Please review all information for accuracy."
    )
    fr.font.size = Pt(8)
    fr.font.color.rgb = _base.COLOR_MUTED
    fr.italic = True

    return _base.finalize(doc)
