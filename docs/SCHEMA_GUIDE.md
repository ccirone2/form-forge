# Schema Guide

A schema is a JSON file that defines the structure of a form. It controls what fields appear, how they're grouped, validation rules, and which template generates the final document.

> **Tip:** You can also create and edit schemas visually using the **Schema tab** — use the JSON editor with live form preview, real-time validation, and right-click context menu to insert field snippets.

## File Location

Place schema files in the `schemas/` directory of your repo:

```
schemas/
├── onboarding.json
├── expense-report.json
└── incident-report.json
```

FormForge discovers schemas automatically when you connect a repo. Each `.json` file in `schemas/` appears as a selectable form in the picker. The file `_schema.spec.json` is reserved for the validator and is excluded from the picker.

## Validation

All schemas are validated against `schemas/_schema.spec.json` (JSON Schema draft 2020-12). The spec enforces `additionalProperties: false` at every level — unknown property names are rejected. CI runs this check automatically on every push.

To validate locally:

```bash
python -c "
import json, jsonschema, pathlib
spec = json.loads(pathlib.Path('schemas/_schema.spec.json').read_text())
for p in pathlib.Path('schemas').glob('*.json'):
    if p.name == '_schema.spec.json': continue
    schema = json.loads(p.read_text())
    jsonschema.validate(schema, spec)
    print(f'OK: {p.name}')
"
```

## Top-Level Structure

```json
{
  "title": "My Form Title",
  "description": "Explains the purpose of this form",
  "icon": "📋",
  "template": "templates/my-form.py",
  "wizard": false,
  "sections": []
}
```

| Property | Required | Type | Description |
|----------|----------|------|-------------|
| `title` | yes | string | Displayed as the form heading. Minimum 1 character. |
| `description` | no | string | Subheading shown below the title and on the picker card. |
| `icon` | no | string | Emoji displayed on the picker card. Defaults to 📄 if omitted. |
| `template` | no | string | Path to the Python template file relative to repo root. Must match `^templates/.+\.py$`. Defaults to `templates/{schema-filename}.py`. |
| `wizard` | no | boolean | When `true`, sections render as sequential steps with Next/Back navigation. See [Wizard Mode](#wizard-mode). |
| `sections` | yes | array | Array of section objects. Minimum 1. |
| `sampleData` | no | object | Inline sample form data (field ID to string value). Used by the **Load Sample Data** button when no fixture file exists. See [Sample Data](#sample-data). |

No other top-level properties are allowed.

## Sections

Sections group related fields together visually. Each section gets its own card in the form UI.

```json
{
  "sections": [
    {
      "title": "Personal Information",
      "fields": [...]
    },
    {
      "title": "Role & Department",
      "fields": [...]
    }
  ]
}
```

| Property | Required | Type | Description |
|----------|----------|------|-------------|
| `title` | yes | string | Section heading displayed above the fields. Minimum 1 character. |
| `fields` | yes | array | Array of field objects. Minimum 1. |
| `step` | no | integer | Step number in wizard mode. Minimum 1. Defaults to section index + 1 if omitted. Only meaningful when `"wizard": true`. |

No other section properties are allowed.

## Fields

Each field defines a single input in the form. The `id` becomes the key in the `data` dictionary passed to the template.

```json
{
  "id": "first_name",
  "label": "First Name",
  "type": "text",
  "required": true,
  "placeholder": "Jane",
  "hint": "As it appears on official documents"
}
```

| Property | Required | Type | Description |
|----------|----------|------|-------------|
| `id` | yes | string | Unique identifier. Pattern: `^[a-z][a-z0-9_]*$`. Becomes `data['first_name']` in the template. |
| `label` | yes | string | Human-readable label displayed above the input. Minimum 1 character. |
| `type` | yes | string | Field type. See [Field Types](#field-types) below. |
| `required` | no | boolean | When `true`, prevents export until the field is filled. |
| `placeholder` | no | string | Ghost text shown inside empty inputs. |
| `hint` | no | string | Help text displayed below the field in smaller text. |
| `options` | conditional | array | Array of strings. Required for `select`, `radio`, `checkbox`, and `multi_select`. Forbidden on all other types. |
| `default_value` | conditional | string | Static value to inject. Required for `hidden`. Forbidden on all other types. |
| `fields` | conditional | array | Sub-field definitions. Required for `repeater`. Forbidden on all other types. |
| `maxLength` | no | integer | Maximum character count. Minimum 1. Allowed on `text` and `longtext` only. On `longtext`, displays a live counter (defaults to 5000). On `text`, schema validation only — no counter in the browser. |
| `min` | no | number | Minimum value. Allowed on `number` only. |
| `max` | no | number | Maximum value. Allowed on `number` only. |
| `step` | no | number | Step increment. Allowed on `number` only. |
| `currency_symbol` | no | string | Currency prefix. Allowed on `currency` only. Defaults to `$`. |
| `accept` | no | string | File type filter (e.g. `"image/*"`). Allowed on `file` only. |
| `max_size_mb` | no | integer | Maximum file size in MB. Minimum 1. Allowed on `file` only. |
| `content` | conditional | string | Display text for `info` blocks. Required for `info`. Forbidden on all other types. |
| `style` | no | string | Visual variant for `info` blocks: `"info"`, `"warning"`, or `"success"`. Defaults to `"info"`. Allowed on `info` only. |
| `min_rows` | no | integer | Minimum rows shown initially. Minimum 1. Allowed on `repeater` only. |
| `max_rows` | no | integer | Maximum rows allowed. Minimum 1. Allowed on `repeater` only. |
| `display` | no | string | Display mode for `repeater`: `"cards"` (default) or `"table"`. Allowed on `repeater` only. |
| `visible_when` | no | object | Conditional visibility rule. See [Conditional Visibility](#conditional-visibility). |

No other field properties are allowed.

## Field IDs

Field IDs must be unique across the entire schema (not just within a section). The pattern `^[a-z][a-z0-9_]*$` means:

- Must start with a lowercase letter
- May contain lowercase letters, digits, and underscores
- No uppercase, no hyphens, no spaces

Examples:

- `first_name` — correct
- `fn` — valid but too cryptic
- `firstName` — rejected (uppercase)
- `first-name` — rejected (hyphen)
- `1name` — rejected (starts with digit)

## Field Types

24 types are supported. The `type` value must be exactly one of these strings.

| Type | Renders As | `options` needed? | Special properties |
|------|-----------|-------------------|--------------------|
| `text` | Single-line input | no | `maxLength` |
| `email` | Email input with browser validation | no | — |
| `tel` | Phone number input | no | — |
| `date` | Native date picker (value: `YYYY-MM-DD`) | no | — |
| `time` | Native time picker (value: `HH:MM`) | no | — |
| `url` | URL input with browser validation | no | — |
| `datetime` | Combined date and time picker | no | — |
| `textarea` | Multi-line text (3 rows) | no | — |
| `longtext` | Large textarea with character counter (6 rows) | no | `maxLength` |
| `select` | Dropdown menu | yes | — |
| `radio` | Radio button group | yes | — |
| `checkbox` | Multi-select checkbox group | yes | — |
| `multi_select` | Searchable multi-select with tags | yes | — |
| `toggle` | Boolean yes/no switch | no | — |
| `list` | Dynamic add/remove rows with bulk paste | no | — |
| `number` | Numeric input | no | `min`, `max`, `step` |
| `currency` | Numeric input with currency prefix | no | `currency_symbol` |
| `heading` | Non-input visual divider | no | — |
| `info` | Read-only info/warning/success block | no | `content` (required), `style` |
| `hidden` | Not rendered; passes static value | no | `default_value` (required) |
| `address` | Street / city / state / ZIP group | no | — |
| `file` | File upload with preview | no | `accept`, `max_size_mb` |
| `signature` | Canvas drawing pad | no | — |
| `repeater` | Dynamic rows of sub-fields | no | `fields` (required), `min_rows`, `max_rows`, `display` |

See `docs/FIELD_TYPES.md` for detailed examples, template handling code, and layout rules for each type.

## Options Arrays

For `select`, `radio`, `checkbox`, and `multi_select` fields, the `options` array defines the available choices:

```json
{
  "id": "department",
  "label": "Department",
  "type": "select",
  "options": ["", "Engineering", "Design", "Marketing", "Sales"]
}
```

For `select` fields, include an empty string `""` as the first option — it renders as "— Select —" and acts as the default unselected state. The empty string fails `required` validation, which prevents submitting without making a selection.

For `radio` and `checkbox`, do not include an empty string.

## Repeater Sub-Fields

The `repeater` type requires a nested `fields` array. Sub-fields support a restricted set of types: `text`, `email`, `tel`, `number`, `currency`, `select`, `time`, `url`, and `toggle`. Sub-field IDs follow the same pattern (`^[a-z][a-z0-9_]*$`) and must be unique within the repeater (they do not need to be unique across the whole schema).

```json
{
  "id": "line_items",
  "label": "Line Items",
  "type": "repeater",
  "min_rows": 1,
  "max_rows": 20,
  "fields": [
    { "id": "description", "label": "Description", "type": "text", "placeholder": "Flight to NYC" },
    { "id": "amount", "label": "Amount", "type": "currency" },
    { "id": "category", "label": "Category", "type": "select", "options": ["", "Travel", "Meals", "Lodging", "Supplies", "Other"] }
  ]
}
```

In the template, the repeater value arrives as a JSON array string. Parse with `json.loads()`.

## Wizard Mode

Setting `"wizard": true` at the top level turns sections into numbered steps with Next/Back navigation. Only one step is visible at a time. The submit area is hidden until the final step.

```json
{
  "title": "Multi-Step Application",
  "wizard": true,
  "sections": [
    {
      "title": "Personal Details",
      "step": 1,
      "fields": [...]
    },
    {
      "title": "Experience",
      "step": 2,
      "fields": [...]
    },
    {
      "title": "Review & Submit",
      "step": 3,
      "fields": [...]
    }
  ]
}
```

The `step` property on each section is optional. If omitted, the step number defaults to the section's position in the array (index + 1). Required field validation is enforced per-step — clicking Next validates only the current step's required fields before advancing.

Non-wizard schemas (no `"wizard"` key, or `"wizard": false`) render all sections on one page as before.

## Conditional Visibility

A field can be hidden until another field has a specific value using `visible_when`:

```json
{
  "id": "other_reason",
  "label": "Please specify",
  "type": "textarea",
  "visible_when": {
    "field": "departure_reason",
    "equals": "Other"
  }
}
```

`visible_when` has two required properties:

| Property | Type | Description |
|----------|------|-------------|
| `field` | string | The `id` of the field whose value controls visibility. Must match `^[a-z][a-z0-9_]*$`. |
| `equals` | string | The exact value that makes this field visible. Case-sensitive. |

No other properties are allowed inside `visible_when`.

Behavior:
- The field is hidden by default and shown only when the referenced field's current value matches `equals`.
- Visibility is evaluated on every `change`/`input` event of the source field.
- Hidden conditional fields are skipped by `required` validation — a hidden field will never block export.
- `collectFormData()` always collects all fields regardless of visibility. Hidden fields contribute an empty string to the data dict.
- The source field can appear anywhere in the schema — before or after the conditional field.
- Multiple fields can each depend on the same source field.

## Layout Behavior

FormForge automatically arranges fields in the form:

- **Two-column rows:** `text`, `email`, `tel`, `date`, `time`, `url`, `datetime`, `select`, `number`, `currency`, and `toggle` fields are paired side-by-side when consecutive.
- **Full-width:** `textarea`, `longtext`, `list`, `radio`, `checkbox`, `multi_select`, `heading`, `info`, `address`, `file`, `signature`, and `repeater` fields always take the full width and break any two-column pairing.
- **Not rendered:** `hidden` fields are completely invisible in the layout.

Control layout by ordering fields intentionally. Two `text` fields in a row pair up. A `text` followed by a `textarea` does not.

## Minimal Example

The smallest valid schema:

```json
{
  "title": "Quick Note",
  "sections": [
    {
      "title": "Note",
      "fields": [
        { "id": "content", "label": "Your Note", "type": "textarea" }
      ]
    }
  ]
}
```

## Sample Data

The **Load Sample Data** button in the form UI lets users fill a form with representative data for quick preview and DOCX testing.

### Fixture files (preferred)

Place a JSON file at `tests/fixtures/{schemaName}_sample.json` where `{schemaName}` matches the schema filename without the `.json` extension (e.g., `schemas/onboarding.json` uses `tests/fixtures/onboarding_sample.json`). The file should contain a flat `{fieldId: stringValue}` object with values for all fields. `file` and `signature` fields can use empty strings.

### Inline `sampleData` (fallback)

If a fixture file is not available (e.g., the schema is hosted in a repo without `tests/fixtures/`), you can include sample data directly in the schema:

```json
{
  "title": "My Form",
  "sampleData": {
    "full_name": "Jane Doe",
    "email": "jane@example.com"
  },
  "sections": [...]
}
```

The button tries the fixture file first, then falls back to `sampleData`.

## Tips

- Start by copying an existing schema (`onboarding.json` or `expense-report.json`) and modifying it.
- Test locally by dropping the `.json` into FormForge's Local Files upload.
- Keep section count reasonable — 3 to 6 sections works well for most forms. If using wizard mode, 3 to 5 steps is a good range.
- Use `hint` generously to guide users, especially for `list`, `longtext`, `repeater`, and `address` fields.
- The `description` field at the top level is worth filling in — it appears in both the picker card and the form header.
- For `select` fields that are also a `visible_when` source, the empty string `""` option means the conditional field is hidden when nothing is selected. Keep this in mind when deciding whether to include the empty option.
