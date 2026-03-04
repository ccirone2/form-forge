# Field Types Reference

Every field in a schema has a `type` that controls how it renders in the form and how its value is passed to the template.

## Quick Reference

| Type | Renders As | Data Format | Needs `options`? |
|------|-----------|-------------|-----------------|
| `text` | Single-line text input | `"Jane"` | no |
| `email` | Email input with browser validation | `"jane@co.com"` | no |
| `tel` | Phone number input | `"(555) 123-4567"` | no |
| `date` | Native date picker | `"2025-03-15"` | no |
| `textarea` | Multi-line text (3 rows) | `"Some notes..."` | no |
| `longtext` | Large textarea with character counter | `"Para 1\nPara 2"` | no |
| `select` | Dropdown menu | `"Engineering"` | yes |
| `radio` | Radio button group | `"Full-Time"` | yes |
| `checkbox` | Checkbox group (multi-select) | `"A, B, C"` | yes |
| `list` | Dynamic add/remove rows with bulk paste | `"X\nY\nZ"` | no |
| `number` | Number input with min/max/step | `"42.5"` | no |
| `currency` | Number input with currency prefix | `"1250.00"` | no |
| `heading` | Non-input section divider | *(skipped)* | no |
| `hidden` | Not rendered (passes static value) | `"1.0"` | no |
| `address` | Multi-field group (street/city/state/zip) | JSON string | no |
| `file` | File upload with preview | base64 data URI | no |
| `signature` | Canvas drawing pad | base64 PNG data URI | no |
| `repeater` | Dynamic group of rows | JSON array string | needs `fields` |

## Layout Rules

Fields are automatically arranged in the form:

- `text`, `email`, `tel`, `date`, `select`, `number`, `currency` — paired into **two-column rows** when consecutive
- `textarea`, `longtext`, `list`, `radio`, `checkbox`, `heading`, `address`, `file`, `signature`, `repeater` — always **full-width**, breaks any pairing
- `hidden` — not rendered in the visible layout at all

You control layout through field ordering. Two consecutive `text` fields pair up. A `text` followed by a `longtext` will not.

---

## text

Standard single-line input. Use for names, titles, short answers.

```json
{ "id": "first_name", "label": "First Name", "type": "text", "required": true, "placeholder": "Jane" }
```

**Template:** `data.get('first_name', '')`  → `"Jane"`

## email

Same as `text` but with browser-level email format validation.

```json
{ "id": "email", "label": "Email Address", "type": "email", "required": true, "placeholder": "jane@company.com" }
```

**Template:** `data.get('email', '')` → `"jane@company.com"`

## tel

Phone number input. No format enforcement — accepts any string.

```json
{ "id": "phone", "label": "Phone", "type": "tel", "placeholder": "(555) 123-4567" }
```

**Template:** `data.get('phone', '')` → `"(555) 123-4567"`

## date

Native browser date picker. Value is always in `YYYY-MM-DD` format.

```json
{ "id": "start_date", "label": "Start Date", "type": "date", "required": true }
```

**Template:** `data.get('start_date', '')` → `"2025-03-15"`

To reformat in your template:

```python
from datetime import datetime
raw = data.get('start_date', '')
if raw:
    formatted = datetime.strptime(raw, '%Y-%m-%d').strftime('%B %d, %Y')
    # "March 15, 2025"
```

## textarea

Multi-line text input, 3 rows tall. Good for short notes or comments.

```json
{ "id": "notes", "label": "Notes", "type": "textarea", "placeholder": "Any additional info..." }
```

**Template:** `data.get('notes', '')` → `"Some notes here"`

## longtext

Large text area (6 rows) with a live character counter. Use for bios, descriptions, or any extended prose. Supports `maxLength` to show a limit.

```json
{
  "id": "bio",
  "label": "Professional Bio",
  "type": "longtext",
  "placeholder": "Write a brief biography...",
  "hint": "This appears as a full paragraph in the document",
  "maxLength": 2000
}
```

**Template:** Value may contain `\n` for paragraph breaks.

```python
bio = data.get('bio', '')
for paragraph in bio.split('\n'):
    if paragraph.strip():
        doc.add_paragraph(paragraph.strip())
```

## select

Dropdown menu. Requires an `options` array.

```json
{
  "id": "department",
  "label": "Department",
  "type": "select",
  "required": true,
  "options": ["", "Engineering", "Design", "Marketing", "Sales"]
}
```

Include `""` as the first option — it renders as "— Select —" and serves as the unselected default. The empty string fails validation if `required` is `true`, which prevents submitting without choosing.

**Template:** `data.get('department', '')` → `"Engineering"`

## radio

Single-choice radio button group. Requires an `options` array. Do not include an empty string.

```json
{
  "id": "employment_type",
  "label": "Employment Type",
  "type": "radio",
  "required": true,
  "options": ["Full-Time", "Part-Time", "Contract", "Intern"]
}
```

**Template:** `data.get('employment_type', '')` → `"Full-Time"`

## checkbox

Multi-select checkbox group. Requires an `options` array. Users can select zero or more items.

```json
{
  "id": "equipment_needs",
  "label": "Additional Equipment",
  "type": "checkbox",
  "options": ["Monitor", "Keyboard", "Mouse", "Standing Desk", "Webcam"],
  "hint": "Select all that apply"
}
```

**Template:** Value is a comma-separated string of selected items.

```python
equipment = data.get('equipment_needs', '')  # "Monitor, Keyboard, Webcam"
if equipment:
    items = [e.strip() for e in equipment.split(',') if e.strip()]
```

## list

Dynamic list entry with two input modes:

- **Individual rows** — click "Add item" or press Enter to add rows. Backspace on an empty row removes it. Each row has an × delete button.
- **Bulk paste** — a textarea where users can paste multiple items separated by newlines, which auto-convert to individual rows.

```json
{
  "id": "skills",
  "label": "Key Skills",
  "type": "list",
  "placeholder": "e.g. Python",
  "hint": "Add skills one at a time or paste multiple"
}
```

**Template:** Value is a newline-separated string.

```python
skills = data.get('skills', '')  # "Python\nJavaScript\nRust"
if skills:
    for item in skills.split('\n'):
        if item.strip():
            doc.add_paragraph(item.strip(), style='List Bullet')
```

## number

Numeric input with optional `min`, `max`, and `step` constraints. Renders as `<input type="number">`.

```json
{ "id": "quantity", "label": "Quantity", "type": "number", "min": 0, "max": 100, "step": 1 }
```

**Schema properties:** `min`, `max`, `step` (all optional).

**Template:** Value is a string — parse with `int()` or `float()` as needed.

```python
qty = int(data.get('quantity', '0'))
```

## currency

Number input with a currency symbol prefix. Defaults to `$` with `step="0.01"`.

```json
{ "id": "total_amount", "label": "Total Amount", "type": "currency", "required": true, "placeholder": "0.00" }
```

**Schema properties:** `currency_symbol` (optional, defaults to `"$"`).

**Template:** Value is a string like `"1250.00"`. Format in the template:

```python
amount = data.get('total_amount', '0')
formatted = f"${float(amount):,.2f}"  # "$1,250.00"
```

## heading

Non-input element that renders as a visual section divider within a form section. Not collected in form data, not passed to templates. Useful for grouping related fields without creating a new schema section.

```json
{ "id": "emergency_heading", "label": "Emergency Contact Information", "type": "heading", "hint": "Provide at least one emergency contact" }
```

**Template:** Not passed — heading fields are skipped during data collection.

## hidden

Invisible field that passes a static value to the template. Use for metadata like form version numbers, form IDs, or computed values.

```json
{ "id": "form_version", "label": "Form Version", "type": "hidden", "default_value": "2.1" }
```

**Schema properties:** `default_value` (the static value to pass).

**Template:** `data.get('form_version', '')` → `"2.1"`

## address

Compound field that renders as a group of 4 sub-inputs: street, city, state, and ZIP code.

```json
{ "id": "mailing_address", "label": "Mailing Address", "type": "address", "hint": "Where should we send it?" }
```

**Template:** Value is a JSON string. Parse it to access sub-fields:

```python
import json
addr = json.loads(data.get('mailing_address', '{}'))
street = addr.get('street', '')
city = addr.get('city', '')
state = addr.get('state', '')
zip_code = addr.get('zip', '')
formatted = f"{street}\n{city}, {state} {zip_code}"
```

**Validation:** When `required`, checks that the street field is non-empty.

## file

File upload input with image preview. The file is read as a base64 data URI and passed to the template.

```json
{
  "id": "receipt_photo",
  "label": "Receipt Photo",
  "type": "file",
  "accept": "image/*",
  "max_size_mb": 5,
  "hint": "Upload a photo of your receipt"
}
```

**Schema properties:**
- `accept` — file type filter (defaults to `"image/*"`)
- `max_size_mb` — maximum file size in MB (defaults to `5`)

**Template:** Value is a base64 data URI string (e.g., `"data:image/png;base64,iVBOR..."`) or empty string.

```python
import base64, io
receipt = data.get('receipt_photo', '')
if receipt and ',' in receipt:
    img_data = receipt.split(',')[1]
    img_bytes = base64.b64decode(img_data)
    doc.add_picture(io.BytesIO(img_bytes), width=Inches(3))
```

## signature

Canvas-based drawing pad for capturing signatures. Supports both mouse and touch input. Exports as a base64 PNG data URI. Includes a "Clear" button to reset.

```json
{ "id": "employee_signature", "label": "Employee Signature", "type": "signature", "required": true }
```

**Template:** Value is a base64 PNG data URI string or empty string. Embed in DOCX:

```python
import base64, io
from docx.shared import Inches
sig = data.get('employee_signature', '')
if sig and ',' in sig:
    sig_bytes = base64.b64decode(sig.split(',')[1])
    doc.add_picture(io.BytesIO(sig_bytes), width=Inches(2.5))
```

## repeater

Dynamic field group — users can add N copies of a set of sub-fields. Ideal for line items, references, dependents, etc.

```json
{
  "id": "line_items",
  "label": "Expense Line Items",
  "type": "repeater",
  "min_rows": 1,
  "max_rows": 20,
  "fields": [
    { "id": "description", "label": "Description", "type": "text", "placeholder": "Flight to NYC" },
    { "id": "amount", "label": "Amount", "type": "currency" },
    { "id": "category", "label": "Category", "type": "select", "options": ["", "Travel", "Meals", "Supplies"] }
  ]
}
```

**Schema properties:**
- `fields` — array of sub-field definitions (supports `text`, `email`, `tel`, `number`, `currency`, `select`)
- `min_rows` — minimum rows shown initially (defaults to `1`)
- `max_rows` — maximum rows allowed (defaults to `10`)

**Template:** Value is a JSON array string. Parse and iterate:

```python
import json
items = json.loads(data.get('line_items', '[]'))
for item in items:
    desc = item.get('description', '')
    amount = item.get('amount', '0')
    category = item.get('category', '')
```

---

## Choosing the Right Type

| If you need... | Use |
|---------------|-----|
| A short answer (name, title, ID) | `text` |
| An email address | `email` |
| A phone number | `tel` |
| A calendar date | `date` |
| A brief comment (1-3 lines) | `textarea` |
| Extended writing (bio, description) | `longtext` |
| One choice from a fixed list | `select` (5+ options) or `radio` (2-4 options) |
| Multiple choices from a fixed list | `checkbox` |
| A user-defined list of items | `list` |
| A numeric value with constraints | `number` |
| A dollar/currency amount | `currency` |
| A visual divider between fields | `heading` |
| Metadata not shown to the user | `hidden` |
| A mailing/physical address | `address` |
| An uploaded image or document | `file` |
| A hand-drawn signature | `signature` |
| Repeated rows of fields (line items) | `repeater` |
