"""
FormForge DOCX Template: Event Registration (Field Type Demo)
=============================================================
Demonstrates all 18 field types, wizard mode, and conditional visibility.

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

import json
from docx.shared import Pt

import stencils


def generate_docx(data: dict[str, str]) -> bytes:
    """
    Generate an Event Registration document from form data.

    Args:
        data: dict mapping field IDs to their string values.

    Returns:
        bytes: The generated .docx file as raw bytes.
    """
    stencils.set_theme(stencils.THEME_MINIMAL)

    name = data.get("full_name", "")
    email = data.get("email", "")
    event_date = data.get("event_date", "")
    form_ver = data.get("form_version", "")

    doc = stencils.new_doc(
        "Event Registration",
        f"{name} — {event_date}",
    )

    # ── Step 1: Applicant Info ────────────────────────────
    stencils.table_section(
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

    stencils.table_section(
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
        stencils.longtext(doc, "Detailed Proposal", proposal)

    # address (conditional — in-person only)
    raw_addr = data.get("venue_address", "{}")
    try:
        addr = json.loads(raw_addr) if raw_addr else {}
    except (json.JSONDecodeError, TypeError):
        addr = {}

    if addr.get("street"):
        stencils.address(doc, "Venue Address", raw_addr)

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

    stencils.table_section(
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

    stencils.repeater_table(
        doc,
        headers=["Item", "Qty", "Unit Cost", "Category"],
        items=items,
        field_keys=["item_name", "quantity", "unit_cost", "category"],
        currency_keys=["unit_cost"],
    )

    # list — special requests
    special = data.get("special_requests", "")
    if special and special.strip():
        stencils.bullet_list(doc, "Special Requests", special)

    # ── Step 4: Attachments & Approval ────────────────────

    # file — supporting document
    doc.add_heading("Supporting Document", level=1)
    stencils.image(
        doc,
        data.get("supporting_doc", ""),
        width_inches=3.0,
        placeholder="No document uploaded.",
    )
    doc.add_paragraph("")

    # textarea — additional notes
    notes = data.get("additional_notes", "")
    if notes and notes.strip():
        stencils.longtext(doc, "Additional Notes", notes)

    # signature — applicant signature
    doc.add_heading("Applicant Signature", level=1)
    stencils.signature(doc, data.get("applicant_signature", ""), "Applicant Signature")
    doc.add_paragraph("")

    # ── Footer ────────────────────────────────────────────
    stencils.footer(doc)

    return stencils.finalize(doc)
