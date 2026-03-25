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

from stencils import Stamp, THEME_CLASSIC


def generate_docx(data: dict[str, str]) -> bytes:
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

    doc = Stamp()
    doc.set_theme(THEME_CLASSIC)
    doc.new_doc(
        "Employee Onboarding Document",
        f"Prepared for {first} {last} — Start Date: {start}",
    )

    # ── Section: Personal Information ──────────────────────────
    doc.table_section(
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
    doc.table_section(
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

    doc.table_section(
        "Equipment & Access",
        [
            ("Laptop", data.get("laptop_preference", "")),
            ("Additional Equipment", equipment if equipment else "None requested"),
            ("Software Access", software if software else "None requested"),
        ],
    )

    # ── Section: Skills & Experience ───────────────────────────
    doc.add_heading("Skills & Experience", level=1)
    doc.longtext("Professional Bio", data.get("bio", ""))
    doc.bullet_list("Key Skills", data.get("skills", ""))
    doc.bullet_list("Certifications & Licenses", data.get("certifications", ""))
    doc.longtext("Notable Prior Projects", data.get("prior_projects", ""))

    # ── Section: Additional Information ────────────────────────
    doc.table_section(
        "Additional Information",
        [
            ("Emergency Contact", data.get("emergency_contact", "")),
            ("Emergency Phone", data.get("emergency_phone", "")),
            ("Dietary Restrictions", data.get("dietary_restrictions", "")),
            ("Notes", data.get("notes", "")),
        ],
    )

    doc.bullet_list("First 90 Days Goals", data.get("onboarding_goals", ""))

    # ── Signatures ─────────────────────────────────────────────
    doc.signatures(
        [
            "Employee Signature",
            "Date",
            "HR Representative",
            "Date",
        ],
    )

    # ── Footer ─────────────────────────────────────────────────
    doc.footer()

    return doc.finalize()
