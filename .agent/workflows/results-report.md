# /results-report Workflow

1. Scan all artifact directories for `metrics.json` outputs:
   - `app/ml_artifacts/disease/metrics.json`
   - `app/ml_artifacts/yield/metrics.json`
   - `app/ml_artifacts/recommend/metrics.json`
   - `app/ml_artifacts/price/metrics.json`
2. Parse metrics values, dataset metadata, and baseline comparisons directly from the JSON files.
3. Check for the presence of evaluation plots in `docs/results/` and artifact folders.
4. If field test evaluation exists (`ml/data/field_test/`), parse field test metrics.
5. Populate and write `docs/results/summary_tables.md` ensuring every single reported figure directly references its source file.
6. Check for limitations (e.g. synthetic data signatures, recursive forecasting error accumulation, lab vs real-world gap) and document them in the report.
