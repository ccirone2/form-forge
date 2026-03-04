"""Tests for FormForge DOCX templates."""

import json
import sys
import importlib.util
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures"
TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

# Add templates/ to path so `import _base` works
sys.path.insert(0, str(TEMPLATES))


def load_template(name):
    spec = importlib.util.spec_from_file_location(name, TEMPLATES / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_onboarding_generates_valid_docx():
    data = json.loads((FIXTURES / "onboarding_sample.json").read_text())
    mod = load_template("onboarding")
    result = mod.generate_docx(data)
    assert isinstance(result, bytes)
    assert len(result) > 0
    assert result[:2] == b"PK"


def test_onboarding_with_empty_data():
    mod = load_template("onboarding")
    result = mod.generate_docx({})
    assert isinstance(result, bytes)
    assert result[:2] == b"PK"


def test_expense_report_generates_valid_docx():
    data = json.loads((FIXTURES / "expense-report_sample.json").read_text())
    mod = load_template("expense-report")
    result = mod.generate_docx(data)
    assert isinstance(result, bytes)
    assert len(result) > 0
    assert result[:2] == b"PK"


def test_expense_report_with_empty_data():
    mod = load_template("expense-report")
    result = mod.generate_docx({})
    assert isinstance(result, bytes)
    assert result[:2] == b"PK"
