# /train-tabular Workflow

1. Verify raw CSV datasets exist in `ml/data/raw/` for yield and crop recommendation.
2. Train yield prediction model:
   - Execute `python ml/train_yield.py`.
   - Run 5-fold cross-validation and evaluate on held-out test split.
   - Compare Linear Regression, Random Forest, and XGBoost against mean baseline.
   - Verify `app/ml_artifacts/yield/pipeline.joblib` and `metrics.json` are written.
3. Train crop recommendation model:
   - Execute `python ml/train_recommend.py`.
   - Run 5-fold cross-validation and evaluate on held-out test split.
   - Compare Random Forest against benchmark classifier.
   - Verify `app/ml_artifacts/recommend/pipeline.joblib`, `metrics.json`, and confusion matrix are written.
4. Verify non-leakage (scalers/encoders fit strictly on train splits).
