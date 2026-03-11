# Field Types Reference

Every field in a schema has a `type` that controls how it renders in the form and how its value is passed to the template.

## Quick Reference

| Type | Renders As | Data Format | Required extra props |
|------|-----------|-------------|----------------------|
| `text` | Single-line text input | `"Jane"` | none |
| `email` | Email input with browser validation | `"jane@co.com"` | none |
| `tel` | Phone number input | `"(555) 123-4567"` | none |
| `date` | Native date picker | `"2025-03-15"` | none |
| `textarea` | Multi-line text (3 rows) | `"Some notes..."` | none |
| `longtext` | Large textarea (6 rows) with character counter | `"Para 1\nPara 2"` | none |
| `select` | Dropdown menu | `"Engineering"` | `options` |
| `radio` | Radio button group | `"Full-Time"` | `options` |
| `checkbox` | Checkbox group (multi-select) | `"A, B, C"` | `options` |
| `list` | Dynamic add/remove rows with bulk paste | `"X\nY\nZ"` | none |
| `number` | Number input with min/max/step | `"42.5"` | none |
| `currency` | Number input with currency prefix | `"1250.00"` | none |
| `heading` | Non-input section divider | *(skipped)* | none |
| `hidden` | Not rendered (passes static value) | `"1.0"` | `default_value` |
| `address` | Multi-field group (street/city/state/zip) | JSON string | none |
| `file` | File upload with preview | base64 data URI | none |
| `signature` | Canvas drawing pad | base64 PNG data URI | none |
| `repeater` | Dynamic group of rows | JSON array string | `fields` |
| `time` | Native time picker | `"09:30"` | none |
| `url` | URL input with browser validation | `"https://example.com"` | none |
| `toggle` | Boolean yes/no switch | `"true"` or `"false"` | none |
| `datetime` | Combined date and time picker | `"2026-06-15T14:30"` | none |
| `multi_select` | Searchable multi-select dropdown with tags | `"A, B, C"` | `options` |

## Common Optional Properties

These apply to any field type unless noted otherwise in the type's section below:

| Property | Type | Description |
|----------|------|-------------|
| `required` | boolean | Fails validation if empty. For `address`, checks that `street` is non-empty. |
| `placeholder` | string | Input placeholder text. Not applicable to `date`, `heading`, `hidden`, `address`, `file`, `signature`, `repeater`. |
| `hint` | string | Helper text shown below the field label. Applicable to all types. |
| `visible_when` | object | Conditionally show this field. See [Conditional Visibility](#conditional-visibility-visible_when). |

## Layout Rules

Fields are automatically arranged in the form:

- `text`, `email`, `tel`, `date`, `select`, `number`, `currency`, `time`, `url`, `toggle`, `datetime` — paired into **two-column rows** when consecutive
- `textarea`, `longtext`, `list`, `radio`, `checkbox`, `heading`, `address`, `file`, `signature`, `repeater`, `multi_select` — always **full-width**, breaks any pairing
- `hidden` — not rendered in the visible layout at all

You control layout through field ordering. Two consecutive `text` fields pair up. A `text` followed by a `longtext` will not.

---

## text

Standard single-line input. Use for names, titles, short answers.

```json
{ "id": "first_name", "label": "First Name", "type": "text", "required": true, "placeholder": "Jane" }
```

**Schema properties:** `maxLength` (optional integer, no enforced limit in the browser — schema validation only).

**Template:** `data.get('first_name', '')` → `"Jane"`

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

Large text area (6 rows) with a live character counter. Use for bios, descriptions, or any extended prose.

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

**Schema properties:** `maxLength` (optional integer, defaults to `5000` in the counter display — does not hard-truncate, only colors the counter red when exceeded).

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

- **Individual rows** — click "Add item" or press Enter to add rows. Backspace on an empty row removes it. Each row has an x delete button.
- **Bulk paste** — a textarea where users can paste multiple items separated by newlines, which auto-convert to individual rows on blur.

One empty row is added automatically when the field renders.

```json
{
  "id": "skills",
  "label": "Key Skills",
  "type": "list",
  "placeholder": "e.g. Python",
  "hint": "Add skills one at a time or paste multiple"
}
```

**Template:** Value is a newline-separated string. Empty list produces `""`.

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

**Schema properties:** `min` (integer), `max` (integer), `step` (number) — all optional. These are the only field types where `min`, `max`, and `step` are permitted; they are forbidden on all other types by the schema spec.

**Template:** Value is a string — parse with `int()` or `float()` as needed.

```python
qty = int(data.get('quantity', '0'))
```

## currency

Number input with a currency symbol prefix. Renders as `<input type="number">` with `step="0.01"` and `min="0"` fixed in the browser.

```json
{ "id": "total_amount", "label": "Total Amount", "type": "currency", "required": true, "placeholder": "0.00" }
```

**Schema properties:** `currency_symbol` (optional string, defaults to `"$"`). This is the only field type where `currency_symbol` is permitted; it is forbidden on all other types by the schema spec.

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

**Template:** Not passed — heading fields are skipped during `collectFormData()`.

**Note:** `heading` does not create an element with `id = field.id`, so it cannot be used as a `visible_when` target.

## hidden

Invisible field that passes a static value to the template. Use for metadata like form version numbers, form IDs, or other values that should appear in the DOCX but not be edited by the user.

```json
{ "id": "form_version", "label": "Form Version", "type": "hidden", "default_value": "2.1" }
```

**Schema properties:** `default_value` (string, required). This is the only field type where `default_value` is permitted; it is forbidden on all other types by the schema spec.

The field group is rendered with `display: none` and the value is restored to `default_value` on form reset.

**Template:** `data.get('form_version', '')` → `"2.1"`

## address

Compound field that renders as a group of 4 sub-inputs: street, city, state, and ZIP code. The sub-inputs use IDs `{field.id}_street`, `{field.id}_city`, `{field.id}_state`, `{field.id}_zip`. There is no single element with `id = field.id`.

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

**Validation:** When `required`, checks that `street` is non-empty.

**Note:** Because there is no element with `id = field.id`, `address` fields cannot reliably be used as `visible_when` targets.

## file

File upload input with image preview. The file is read as a base64 data URI and stored in a hidden input with `id = field.id`.

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
- `accept` — file type filter passed to `<input type="file" accept="...">` (defaults to `"image/*"`)
- `max_size_mb` — maximum file size in MB, enforced client-side (defaults to `5`)

Non-image files are accepted (based on `accept`) but won't show a preview. Image files show a preview inline.

**Template:** Value is a base64 data URI string (e.g., `"data:image/png;base64,iVBOR..."`) or empty string if no file was uploaded.

```python
import base64, io
receipt = data.get('receipt_photo', '')
if receipt and ',' in receipt:
    img_data = receipt.split(',')[1]
    img_bytes = base64.b64decode(img_data)
    doc.add_picture(io.BytesIO(img_bytes), width=Inches(3))
```

## signature

Canvas-based drawing pad for capturing signatures. Supports both mouse and touch input. The canvas is 400x150 pixels internally. Exports as a base64 PNG data URI stored in a hidden input with `id = field.id`. Includes a "Clear" button to reset.

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

Dynamic field group — users can add N copies of a set of sub-fields. Each row is numbered and has a remove button. Ideal for line items, references, dependents, etc.

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
- `fields` — required array of sub-field definitions. Permitted sub-field types: `text`, `email`, `tel`, `number`, `currency`, `select`. No other types (including `heading`, `hidden`, `address`, `repeater`) are allowed inside a repeater.
- `min_rows` — minimum rows; remove button is disabled when at the minimum (defaults to `1`)
- `max_rows` — maximum rows; add button is disabled when at the maximum (defaults to `10`)

Sub-field IDs within `fields` must be unique within the repeater but do not need to be globally unique. They are keyed by sub-field `id` in each row's data object.

**Template:** Value is a JSON array string. Parse and iterate:

```python
import json
items = json.loads(data.get('line_items', '[]'))
for item in items:
    desc = item.get('description', '')
    amount = item.get('amount', '0')
    category = item.get('category', '')
```

## time

Native browser time picker. Value is always in `HH:MM` format (24-hour).

```json
{ "id": "start_time", "label": "Start Time", "type": "time", "required": true }
```

**Template:** `data.get('start_time', '')` → `"09:30"`

To reformat in your template:

```python
formatted = stencils.format_time(data.get('start_time', ''))
# "09:30" → "9:30 AM", "14:30" → "2:30 PM"
```

## url

URL input with browser-level URL format validation. Includes `https://` placeholder by default.

```json
{ "id": "website", "label": "Website", "type": "url", "placeholder": "https://example.com" }
```

**Template:** `data.get('website', '')` → `"https://example.com"`

## toggle

Boolean yes/no switch. Renders as a toggle switch UI element. Distinct from `checkbox` which is a multi-select group — `toggle` is a single on/off control.

```json
{ "id": "agree_terms", "label": "I agree to the terms", "type": "toggle", "required": true }
```

The toggle always has a value (`"true"` or `"false"`) — it can never be empty. A required toggle will always pass validation.

**Template:** Value is `"true"` or `"false"`.

```python
agreed = data.get('agree_terms', 'false') == 'true'
doc.add_paragraph(f"Terms accepted: {'Yes' if agreed else 'No'}")
```

## datetime

Combined date and time picker. Renders as `<input type="datetime-local">`. Value is in ISO-like format `YYYY-MM-DDTHH:MM`.

```json
{ "id": "deadline", "label": "Submission Deadline", "type": "datetime" }
```

**Template:** `data.get('deadline', '')` → `"2026-06-15T14:30"`

To reformat in your template:

```python
formatted = stencils.format_time(data.get('deadline', ''))
# "2026-06-15T14:30" → "2026-06-15 at 2:30 PM"
```

## multi_select

Searchable multi-select dropdown with tag/chip UI. Requires an `options` array. Users can select multiple items, which appear as removable tags. Includes a search/filter input.

```json
{
  "id": "topics",
  "label": "Topics of Interest",
  "type": "multi_select",
  "options": ["AI/ML", "Cloud", "Security", "DevOps", "Frontend", "Backend"],
  "hint": "Select all that apply"
}
```

Distinct from `checkbox`: `multi_select` is better for long option lists (5+ items) because it includes search filtering and takes less vertical space. Use `checkbox` for short lists (2-5 items) where all options should be visible at once.

**Template:** Value is a comma-separated string of selected items, same format as `checkbox`.

```python
topics = data.get('topics', '')  # "AI/ML, Cloud, Security"
if topics:
    items = [t.strip() for t in topics.split(',') if t.strip()]
```

---

## Conditional Visibility (`visible_when`)

Any top-level field can include a `visible_when` object to make it appear only when another field has a specific value.

```json
{
  "id": "contract_end_date",
  "label": "Contract End Date",
  "type": "date",
  "visible_when": { "field": "employment_type", "equals": "Contract" }
}
```

**Schema:**

```json
"visible_when": {
  "field": "employment_type",   // id of the controlling field
  "equals": "Contract"          // value that makes this field visible
}
```

**Behavior:** Hidden fields start with CSS class `conditional-hidden` (display: none). When the controlling field's value matches `equals`, the class is removed. The comparison is a strict string equality check on the field's current value.

**When required fields are hidden:** Validation skips them. `isFieldConditionallyHidden()` checks the field group's CSS class, so hidden-but-required fields do not block form submission.

**Supported source field types** (the `field` being watched):
- `select` — attaches a `change` listener on the `<select>` element
- `radio` — attaches `change` listeners on all `<input type="radio">` elements for that name
- `checkbox` — attaches `change` listeners; `equals` must match the full comma-separated string of checked values
- `text`, `email`, `tel`, `date`, `time`, `url`, `datetime`, `textarea`, `longtext`, `number`, `currency` — attaches `input` and `change` listeners on the element
- `toggle` — attaches a `change` listener on the checkbox input

**Supported target field types** (the field with `visible_when`):
Works for any type that renders a direct element with `id = field.id`: `text`, `email`, `tel`, `date`, `time`, `url`, `datetime`, `textarea`, `longtext`, `select`, `number`, `currency`, `hidden`, `file`, `signature`, `toggle`.

Does **not** reliably work as a target for: `checkbox`, `radio`, `list`, `address`, `repeater`, `heading`, `multi_select` — these types do not render a single element with `id = field.id`, so the visibility logic cannot find their field group.

`visible_when` is not supported inside `repeater` sub-fields.

---

## Choosing the Right Type

| If you need... | Use |
|---------------|-----|
| A short answer (name, title, ID) | `text` |
| An email address | `email` |
| A phone number | `tel` |
| A website or link | `url` |
| A calendar date | `date` |
| A clock time | `time` |
| A date and time together | `datetime` |
| A brief comment (1-3 lines) | `textarea` |
| Extended writing (bio, description) | `longtext` |
| One choice from a fixed list | `select` (5+ options) or `radio` (2-4 options) |
| Multiple choices from a short list | `checkbox` (2-5 options visible at once) |
| Multiple choices from a long list | `multi_select` (5+ options, with search) |
| A yes/no boolean answer | `toggle` |
| A user-defined list of items | `list` |
| A numeric value with constraints | `number` |
| A dollar/currency amount | `currency` |
| A visual divider between fields | `heading` |
| Metadata not shown to the user | `hidden` |
| A mailing/physical address | `address` |
| An uploaded image or document | `file` |
| A hand-drawn signature | `signature` |
| Repeated rows of fields (line items) | `repeater` |
