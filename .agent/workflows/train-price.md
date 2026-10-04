# /train-price Workflow

1. Verify mandi price time-series dataset exists in `ml/data/raw/`.
2. Inspect date granularity, missing dates, and length of history per crop.
3. Execute `python ml/train_price.py`.
4. Enforce strict chronological train/test split (no shuffling) and train-only scaler fitting.
5. For each crop with sufficient history:
   - Train LSTM architecture: `LSTM(50, return_sequences=True) -> LSTM(50) -> Dense(25) -> Dense(1)` with early stopping.
   - Fit Naive last-value baseline and ARIMA/Holt-Winters models.
   - Evaluate multi-step recursive 7-day forecast (MAE, RMSE, MAPE).
   - Save model artifacts to `app/ml_artifacts/price/<crop>/` and write forecast-vs-actual comparison plots.
6. Write combined `app/ml_artifacts/price/metrics.json` and report comparison table for Checkpoint 4c.
