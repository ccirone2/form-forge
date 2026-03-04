"""
FormForge DOCX Template: Employee Onboarding Document
======================================================
This script is loaded by FormForge's Pyodide runtime.
It must export a `generate_docx(data)` function that accepts
a dict of form field values and returns docx file bytes.

The `data` dict keys match the field `id` values in the
corresponding schema JSON (schemas/onboarding.json).

Field type notes:
  - text/email/tel/date/select/radio/textarea → str
  - checkbox → comma-separated str (e.g. "GitHub, Jira, Figma")
  - longtext → str with possible newlines for paragraphs
  - list → newline-separated str (e.g. "Python\\nJavaScript\\nRust")
"""

import _base


def generate_docx(data):
    """
    Generate an Employee Onboarding Document from form data.

    Args:
        data: dict mapping field IDs to their string values.

    Returns:
        bytes: The generated .docx file as raw bytes.
    """
    first = data.get("first_name", "")
    last = data.get("last_name", "")
    start = data.get("start_date", "TBD")

    doc = _base.new_doc(
        "Employee Onboarding Document",
        f"Prepared for {first} {last} — Start Date: {start}",
    )

    # ── Section: Personal Information ──────────────────────────
    _base.add_table_section(
        doc,
        "Personal Information",
        [
            ("First Name", data.get("first_name", "")),
            ("Last Name", data.get("last_name", "")),
            ("Email", data.get("email", "")),
            ("Phone", data.get("phone", "")),
            ("Date of Birth", data.get("date_of_birth", "")),
            ("Start Date", data.get("start_date", "")),
        ],
    )

    # ── Section: Role & Department ─────────────────────────────
    _base.add_table_section(
        doc,
        "Role & Department",
        [
            ("Department", data.get("department", "")),
            ("Job Title", data.get("job_title", "")),
            ("Employment Type", data.get("employment_type", "")),
            ("Reporting Manager", data.get("manager", "")),
        ],
    )

    # ── Section: Equipment & Access ────────────────────────────
    equipment = data.get("equipment_needs", "")
    software = data.get("software_access", "")

    _base.add_table_section(
        doc,
        "Equipment & Access",
        [
            ("Laptop", data.get("laptop_preference", "")),
            ("Additional Equipment", equipment if equipment else "None requested"),
            ("Software Access", software if software else "None requested"),
        ],
    )

    # ── Section: Skills & Experience ───────────────────────────
    doc.add_heading("Skills & Experience", level=1)

    _base.add_longtext(doc, "Professional Bio", data.get("bio", ""))
    _base.add_bullet_list(doc, "Key Skills", data.get("skills", ""))
    _base.add_bullet_list(
        doc, "Certifications & Licenses", data.get("certifications", "")
    )
    _base.add_longtext(doc, "Notable Prior Projects", data.get("prior_projects", ""))

    # ── Section: Additional Information ────────────────────────
    _base.add_table_section(
        doc,
        "Additional Information",
        [
            ("Dietary Restrictions", data.get("dietary_restrictions", "")),
            ("Emergency Contact", data.get("emergency_contact", "")),
            ("Emergency Phone", data.get("emergency_phone", "")),
            ("Notes", data.get("notes", "")),
        ],
    )

    _base.add_bullet_list(doc, "First 90 Days Goals", data.get("onboarding_goals", ""))

    # ── Signatures ─────────────────────────────────────────────
    _base.add_signatures(
        doc,
        [
            "Employee Signature",
            "Date",
            "HR Representative",
            "Date",
        ],
    )

    # ── Footer ─────────────────────────────────────────────────
    _base.add_footer(doc)

    return _base.finalize(doc)
