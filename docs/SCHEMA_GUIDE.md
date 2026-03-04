# Schema Guide

A schema is a JSON file that defines the structure of a form. It controls what fields appear, how they're grouped, validation rules, and which template generates the final document.

## File Location

Place schema files in the `schemas/` directory of your repo:

```
schemas/
├── onboarding.json
├── expense-report.json
└── incident-report.json
```

FormForge discovers schemas automatically when you connect a repo. Each `.json` file in `schemas/` appears as a selectable form in the picker.

## Top-Level Structure

```json
{
  "title": "My Form Title",
  "description": "Explains the purpose of this form",
  "icon": "📋",
  "template": "templates/my-form.py",
  "sections": []
}
```

| Property | Required | Description |
|----------|----------|-------------|
| `title` | yes | Displayed as the form heading |
| `description` | no | Subheading shown below the title |
| `icon` | no | Emoji displayed on the picker card (defaults to 📄) |
| `template` | no | Path to the Python template file. Defaults to `templates/{schema-name}.py` if omitted |
| `sections` | yes | Array of section objects that contain the form fields |

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

| Property | Required | Description |
|----------|----------|-------------|
| `title` | yes | Section heading displayed above the fields |
| `fields` | yes | Array of field objects |

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

| Property | Required | Description |
|----------|----------|-------------|
| `id` | yes | Unique identifier. Use `snake_case`. This becomes `data['first_name']` in the template |
| `label` | yes | Human-readable label displayed above the input |
| `type` | yes | Field type — see [Field Types](FIELD_TYPES.md) for the full list |
| `required` | no | Set to `true` to prevent export until this field is filled |
| `placeholder` | no | Ghost text shown inside empty inputs |
| `hint` | no | Help text displayed below the field in smaller text |
| `options` | conditional | Array of strings. Required for `select`, `radio`, and `checkbox` types |
| `maxLength` | no | Maximum character count for `longtext` fields. Displays a live counter |

## Field IDs

Field IDs must be unique across the entire schema (not just within a section). They should use `snake_case` and be descriptive:

- `first_name` — good
- `fn` — too cryptic
- `firstName` — works but inconsistent with Python conventions
- `first_name_2` — fine if you have two name fields for different purposes

## Options Arrays

For `select`, `radio`, and `checkbox` fields, the `options` array defines the available choices:

```json
{
  "id": "department",
  "label": "Department",
  "type": "select",
  "options": ["", "Engineering", "Design", "Marketing", "Sales"]
}
```

For `select` fields, include an empty string `""` as the first option — it renders as "— Select —" and acts as the default unselected state.

For `radio` and `checkbox`, do not include an empty string.

## Layout Behavior

FormForge automatically arranges fields in the form:

- **Two-column rows:** `text`, `email`, `tel`, `date`, and `select` fields are paired side-by-side when consecutive
- **Full-width:** `textarea`, `longtext`, `list`, `radio`, and `checkbox` fields always take the full width and break any two-column pairing

You can control layout by ordering fields intentionally. Two `text` fields in a row will pair up. A `text` followed by a `textarea` will not.

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

## Tips

- Start by copying an existing schema and modifying it
- Test locally by dropping the `.json` into FormForge's Local Files upload
- Keep section count reasonable — 3 to 6 sections works well for most forms
- Use `hint` generously to guide users, especially for `list` and `longtext` fields
- The `description` field at the top level is worth filling in — it appears in both the picker card and the form header
