"""Tests for schema validation against _schema.spec.json."""

import json
from pathlib import Path

import jsonschema
import pytest

SCHEMAS_DIR = Path(__file__).resolve().parent.parent / "schemas"
SPEC_PATH = SCHEMAS_DIR / "_schema.spec.json"


def _load_spec():
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def _schema_files():
    """Return all .json files in schemas/ except the spec itself."""
    return sorted(
        p for p in SCHEMAS_DIR.glob("*.json") if p.name != "_schema.spec.json"
    )


def test_spec_is_valid_json_schema():
    """The spec file itself must be a valid JSON Schema (draft 2020-12)."""
    spec = _load_spec()
    assert spec["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    # Validate the meta-schema (checks the spec is well-formed)
    jsonschema.Draft202012Validator.check_schema(spec)


def test_spec_requires_title_and_sections():
    spec = _load_spec()
    assert "title" in spec["required"]
    assert "sections" in spec["required"]


def test_spec_enumerates_all_field_types():
    spec = _load_spec()
    expected_types = {
        "text",
        "email",
        "tel",
        "date",
        "textarea",
        "longtext",
        "select",
        "radio",
        "checkbox",
        "list",
        "number",
        "currency",
        "heading",
        "hidden",
        "address",
        "file",
        "signature",
        "repeater",
        "time",
        "url",
        "toggle",
        "datetime",
        "multi_select",
    }
    actual_types = set(spec["$defs"]["fieldType"]["enum"])
    assert actual_types == expected_types


def test_validate_onboarding_schema():
    spec = _load_spec()
    schema = json.loads((SCHEMAS_DIR / "onboarding.json").read_text(encoding="utf-8"))
    jsonschema.validate(instance=schema, schema=spec)


def test_validate_expense_report_schema():
    spec = _load_spec()
    schema = json.loads(
        (SCHEMAS_DIR / "expense-report.json").read_text(encoding="utf-8")
    )
    jsonschema.validate(instance=schema, schema=spec)


def test_validate_all_schemas():
    """Every schema file in schemas/ must validate against the spec."""
    spec = _load_spec()
    schema_files = _schema_files()
    assert len(schema_files) > 0, "No schema files found"
    for path in schema_files:
        schema = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.validate(instance=schema, schema=spec)


# --- Negative tests: schemas that SHOULD fail ---


def test_rejects_missing_title():
    spec = _load_spec()
    bad = {
        "sections": [
            {"title": "S", "fields": [{"id": "x", "label": "X", "type": "text"}]}
        ]
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_empty_sections():
    spec = _load_spec()
    bad = {"title": "T", "sections": []}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_invalid_field_id():
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [{"id": "BadId", "label": "X", "type": "text"}],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_unknown_field_type():
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [{"id": "x", "label": "X", "type": "foobar"}],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_select_without_options():
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [{"id": "x", "label": "X", "type": "select"}],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_hidden_without_default_value():
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [{"id": "x", "label": "X", "type": "hidden"}],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_repeater_without_fields():
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [{"id": "x", "label": "X", "type": "repeater"}],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_options_on_text_field():
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [{"id": "x", "label": "X", "type": "text", "options": ["a"]}],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_min_on_text_field():
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [{"id": "x", "label": "X", "type": "text", "min": 0}],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


# --- Wizard schema tests ---


def test_wizard_schema_validates():
    """A schema with wizard: true and step on sections should validate."""
    spec = _load_spec()
    wizard_schema = {
        "title": "Wizard Form",
        "wizard": True,
        "sections": [
            {
                "title": "Step 1",
                "step": 1,
                "fields": [{"id": "name", "label": "Name", "type": "text"}],
            },
            {
                "title": "Step 2",
                "step": 2,
                "fields": [{"id": "email", "label": "Email", "type": "email"}],
            },
        ],
    }
    jsonschema.validate(instance=wizard_schema, schema=spec)


def test_wizard_schema_without_step_validates():
    """A wizard schema where sections omit step should still validate."""
    spec = _load_spec()
    wizard_schema = {
        "title": "Wizard Form",
        "wizard": True,
        "sections": [
            {
                "title": "Part A",
                "fields": [{"id": "x", "label": "X", "type": "text"}],
            },
            {
                "title": "Part B",
                "fields": [{"id": "y", "label": "Y", "type": "text"}],
            },
        ],
    }
    jsonschema.validate(instance=wizard_schema, schema=spec)


def test_non_wizard_schemas_still_validate():
    """Existing schemas without wizard flag must continue to validate."""
    spec = _load_spec()
    schema_files = _schema_files()
    assert len(schema_files) > 0
    for path in schema_files:
        schema = json.loads(path.read_text(encoding="utf-8"))
        assert "wizard" not in schema or isinstance(schema.get("wizard"), bool)
        jsonschema.validate(instance=schema, schema=spec)


def test_rejects_wizard_non_boolean():
    """wizard must be a boolean, not a string or int."""
    spec = _load_spec()
    bad = {
        "title": "T",
        "wizard": "yes",
        "sections": [
            {
                "title": "S",
                "fields": [{"id": "x", "label": "X", "type": "text"}],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_step_non_integer():
    """step must be a positive integer, not a string."""
    spec = _load_spec()
    bad = {
        "title": "T",
        "wizard": True,
        "sections": [
            {
                "title": "S",
                "step": "one",
                "fields": [{"id": "x", "label": "X", "type": "text"}],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_step_zero():
    """step must be >= 1."""
    spec = _load_spec()
    bad = {
        "title": "T",
        "wizard": True,
        "sections": [
            {
                "title": "S",
                "step": 0,
                "fields": [{"id": "x", "label": "X", "type": "text"}],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


# --- visible_when tests ---


def test_visible_when_validates():
    """A field with visible_when should validate."""
    spec = _load_spec()
    schema = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [
                    {
                        "id": "color",
                        "label": "Color",
                        "type": "select",
                        "options": ["Red", "Blue", "Other"],
                    },
                    {
                        "id": "other_color",
                        "label": "Describe color",
                        "type": "text",
                        "visible_when": {"field": "color", "equals": "Other"},
                    },
                ],
            }
        ],
    }
    jsonschema.validate(instance=schema, schema=spec)


def test_rejects_visible_when_missing_field():
    """visible_when must have a 'field' property."""
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [
                    {
                        "id": "x",
                        "label": "X",
                        "type": "text",
                        "visible_when": {"equals": "yes"},
                    }
                ],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_visible_when_missing_equals():
    """visible_when must have an 'equals' property."""
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [
                    {
                        "id": "x",
                        "label": "X",
                        "type": "text",
                        "visible_when": {"field": "y"},
                    }
                ],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_visible_when_extra_property():
    """visible_when must not have extra properties."""
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [
                    {
                        "id": "x",
                        "label": "X",
                        "type": "text",
                        "visible_when": {
                            "field": "y",
                            "equals": "yes",
                            "operator": "eq",
                        },
                    }
                ],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_existing_schemas_still_validate_after_visible_when():
    """Regression: all existing schemas must still validate."""
    spec = _load_spec()
    for path in _schema_files():
        schema = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.validate(instance=schema, schema=spec)


# ---------------------------------------------------------------------------
#  sampleData property
# ---------------------------------------------------------------------------


def _minimal_schema():
    """Return a minimal valid schema for testing."""
    return {
        "title": "Test Form",
        "sections": [
            {
                "title": "Section 1",
                "fields": [{"id": "name", "label": "Name", "type": "text"}],
            }
        ],
    }


def test_sample_data_validates():
    """A schema with an optional sampleData object should validate."""
    spec = _load_spec()
    schema = _minimal_schema()
    schema["sampleData"] = {"name": "Jane Doe"}
    jsonschema.validate(instance=schema, schema=spec)


def test_sample_data_is_optional():
    """Schemas without sampleData must still validate (it's optional)."""
    spec = _load_spec()
    schema = _minimal_schema()
    assert "sampleData" not in schema
    jsonschema.validate(instance=schema, schema=spec)


def test_rejects_sample_data_non_object():
    """sampleData must be an object, not a string or array."""
    spec = _load_spec()
    schema = _minimal_schema()
    schema["sampleData"] = "not an object"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=schema, schema=spec)


# ---------------------------------------------------------------------------
#  min/max float support
# ---------------------------------------------------------------------------


def test_number_field_accepts_float_min_max():
    """min/max on a number field should accept float values like 0.5."""
    spec = _load_spec()
    schema = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [
                    {
                        "id": "rating",
                        "label": "Rating",
                        "type": "number",
                        "min": 0.5,
                        "max": 9.5,
                        "step": 0.5,
                    }
                ],
            }
        ],
    }
    jsonschema.validate(instance=schema, schema=spec)


# ---------------------------------------------------------------------------
#  repeaterField exclusion rules
# ---------------------------------------------------------------------------


def test_rejects_min_on_select_repeater_field():
    """min is not allowed on a select repeater sub-field."""
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [
                    {
                        "id": "items",
                        "label": "Items",
                        "type": "repeater",
                        "fields": [
                            {
                                "id": "cat",
                                "label": "Category",
                                "type": "select",
                                "options": ["A", "B"],
                                "min": 1,
                            }
                        ],
                    }
                ],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_currency_symbol_on_text_repeater_field():
    """currency_symbol is not allowed on a text repeater sub-field."""
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [
                    {
                        "id": "items",
                        "label": "Items",
                        "type": "repeater",
                        "fields": [
                            {
                                "id": "name",
                                "label": "Name",
                                "type": "text",
                                "currency_symbol": "$",
                            }
                        ],
                    }
                ],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_max_length_on_number_repeater_field():
    """maxLength is not allowed on a number repeater sub-field."""
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [
                    {
                        "id": "items",
                        "label": "Items",
                        "type": "repeater",
                        "fields": [
                            {
                                "id": "qty",
                                "label": "Qty",
                                "type": "number",
                                "maxLength": 5,
                            }
                        ],
                    }
                ],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_repeater_number_field_accepts_min_max():
    """min/max/step should be allowed on a number repeater sub-field."""
    spec = _load_spec()
    schema = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [
                    {
                        "id": "items",
                        "label": "Items",
                        "type": "repeater",
                        "fields": [
                            {
                                "id": "qty",
                                "label": "Qty",
                                "type": "number",
                                "min": 1,
                                "max": 100,
                                "step": 1,
                            }
                        ],
                    }
                ],
            }
        ],
    }
    jsonschema.validate(instance=schema, schema=spec)


# ---------------------------------------------------------------------------
#  Duplicate field ID check
# ---------------------------------------------------------------------------


def _collect_all_ids(schema):
    """Collect all field IDs from a schema, including repeater sub-fields."""
    ids = []
    for section in schema.get("sections", []):
        for field in section.get("fields", []):
            ids.append(field["id"])
            for sub in field.get("fields", []):
                ids.append(sub["id"])
    return ids


# ---------------------------------------------------------------------------
#  New field types: time, url, toggle, datetime, multi_select
# ---------------------------------------------------------------------------


def test_time_field_validates():
    spec = _load_spec()
    schema = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [{"id": "start_time", "label": "Start Time", "type": "time"}],
            }
        ],
    }
    jsonschema.validate(instance=schema, schema=spec)


def test_url_field_validates():
    spec = _load_spec()
    schema = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [
                    {
                        "id": "website",
                        "label": "Website",
                        "type": "url",
                        "placeholder": "https://example.com",
                    }
                ],
            }
        ],
    }
    jsonschema.validate(instance=schema, schema=spec)


def test_toggle_field_validates():
    spec = _load_spec()
    schema = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [
                    {
                        "id": "agree",
                        "label": "Agree?",
                        "type": "toggle",
                        "required": True,
                    }
                ],
            }
        ],
    }
    jsonschema.validate(instance=schema, schema=spec)


def test_datetime_field_validates():
    spec = _load_spec()
    schema = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [{"id": "deadline", "label": "Deadline", "type": "datetime"}],
            }
        ],
    }
    jsonschema.validate(instance=schema, schema=spec)


def test_multi_select_field_validates():
    spec = _load_spec()
    schema = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [
                    {
                        "id": "topics",
                        "label": "Topics",
                        "type": "multi_select",
                        "options": ["AI", "Cloud", "Security"],
                    }
                ],
            }
        ],
    }
    jsonschema.validate(instance=schema, schema=spec)


def test_rejects_multi_select_without_options():
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [{"id": "topics", "label": "Topics", "type": "multi_select"}],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_options_on_toggle():
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [
                    {
                        "id": "agree",
                        "label": "Agree",
                        "type": "toggle",
                        "options": ["Yes", "No"],
                    }
                ],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_rejects_options_on_time():
    spec = _load_spec()
    bad = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [
                    {
                        "id": "t",
                        "label": "T",
                        "type": "time",
                        "options": ["09:00"],
                    }
                ],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=spec)


def test_repeater_with_time_url_toggle():
    """time, url, and toggle are valid repeater sub-field types."""
    spec = _load_spec()
    schema = {
        "title": "T",
        "sections": [
            {
                "title": "S",
                "fields": [
                    {
                        "id": "items",
                        "label": "Items",
                        "type": "repeater",
                        "fields": [
                            {"id": "start", "label": "Start", "type": "time"},
                            {"id": "link", "label": "Link", "type": "url"},
                            {"id": "done", "label": "Done", "type": "toggle"},
                        ],
                    }
                ],
            }
        ],
    }
    jsonschema.validate(instance=schema, schema=spec)


def test_no_duplicate_field_ids():
    """Every schema must have unique field IDs across all sections."""
    for path in _schema_files():
        schema = json.loads(path.read_text(encoding="utf-8"))
        ids = _collect_all_ids(schema)
        dupes = [i for i in ids if ids.count(i) > 1]
        assert len(ids) == len(set(ids)), f"Duplicate field IDs in {path.name}: {dupes}"
