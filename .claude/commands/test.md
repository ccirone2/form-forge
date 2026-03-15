# Run Tests

Run the FormForge test suite.

If $ARGUMENTS is "all":
  Run all tests including e2e browser tests: `PYTHONPATH=. python -m pytest tests/ -v -m ''`
Else if $ARGUMENTS is "e2e":
  Run only e2e browser tests: `PYTHONPATH=. python -m pytest tests/ -v -m e2e`
Else:
  Run fast tests (excludes e2e): `PYTHONPATH=. python -m pytest tests/ -v`

Report the results with pass/fail counts.
