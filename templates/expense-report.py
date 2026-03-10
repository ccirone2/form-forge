"""
FormForge DOCX Template: Expense Report
========================================
Demonstrates all new field types (number, currency, heading, hidden,
address, file, signature, repeater) alongside existing types.

Field type notes:
  - text/email/tel/date/select/radio/textarea → str
  - number/currency → str (e.g. "42.5", "1250.00")
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

import stencils


def generate_docx(data):
    """
    Generate an Expense Report Document from form data.

    Args:
        data: dict mapping field IDs to their string values.

    Returns:
        bytes: The generated .docx file as raw bytes.
    """
    name = data.get("employee_name", "")
    dept = data.get("department", "")
    report_date = data.get("report_date", "")
    form_ver = data.get("form_version", "")

    doc = stencils.new_doc(
        "Expense Report",
        f"{name} — {dept} — {report_date}",
    )

    # ── Report Details ──────────────────────────────────────
    total = data.get("total_amount", "0")
    try:
        total_fmt = f"${float(total):,.2f}"
    except (ValueError, TypeError):
        total_fmt = f"${total}"

    stencils.table_section(
        doc,
        "Report Details",
        [
            ("Employee", name),
            ("Department", dept),
            ("Report Date", report_date),
            ("Total Amount", total_fmt),
            ("Form Version", form_ver),
        ],
    )

    # ── Line Items (repeater) ───────────────────────────────
    doc.add_heading("Expense Line Items", level=1)

    raw_items = data.get("line_items", "[]")
    try:
        items = json.loads(raw_items)
    except (json.JSONDecodeError, TypeError):
        items = []

    stencils.repeater_table(
        doc,
        headers=["Description", "Amount", "Category"],
        items=items,
        field_keys=["description", "amount", "category"],
        currency_keys=["amount"],
    )

    # ── Number of Receipts (number field) ───────────────────
    stencils.table_section(
        doc,
        "Receipts",
        [("Number of receipts attached", data.get("item_count", "0"))],
    )

    # ── Receipt Photo (file field) ──────────────────────────
    doc.add_heading("Receipt / Invoice", level=1)
    stencils.image(
        doc,
        data.get("receipt_photo", ""),
        width_inches=3.0,
        placeholder="No receipt uploaded.",
    )
    doc.add_paragraph("")

    # ── Notes ───────────────────────────────────────────────
    notes = data.get("notes", "")
    if notes and notes.strip():
        stencils.longtext(doc, "Additional Notes", notes)

    # ── Mailing Address (address field) ─────────────────────
    stencils.address(
        doc,
        "Reimbursement Mailing Address",
        data.get("mailing_address", "{}"),
    )

    # ── Signatures (signature fields) ───────────────────────
    doc.add_heading("Approval Signatures", level=1)
    for label, field_id in [
        ("Employee Signature", "employee_signature"),
        ("Manager Signature", "manager_signature"),
    ]:
        stencils.signature(doc, data.get(field_id, ""), label)
    doc.add_paragraph("")

    # ── Footer ──────────────────────────────────────────────
    stencils.footer(doc)

    return stencils.finalize(doc)
