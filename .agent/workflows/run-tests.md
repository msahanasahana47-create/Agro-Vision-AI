# /run-tests Workflow

1. Ensure the Python environment has all test requirements installed.
2. Run pytest suite with verbose output:
   `pytest -v tests/`
3. If failures occur:
   - Identify whether the root cause is in a service, model artifact, or route handler.
   - Formulate proposed fix and implement corrections.
   - Re-run pytest until all tests pass with 0 failures.
4. Record test execution log and coverage metrics.
