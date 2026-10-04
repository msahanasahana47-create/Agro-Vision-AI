"""Mandi price time series forecasting service."""
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone

_PRICE_MODELS = {}
SUPPORTED_CROPS = ["rice", "wheat", "maize", "cotton", "potato", "onion", "tomato"]


def init_price_models(artifacts_dir: Path) -> None:
    """Load per-crop price forecasting models once at app startup."""
    global _PRICE_MODELS
    price_dir = artifacts_dir / "price"
    if not price_dir.exists():
        return
    # Loading logic implemented in M5


def forecast_price(crop: str) -> Dict[str, Any]:
    """Forecast mandi price for 7 days ahead with historical chart data and baseline comparison."""
    normalized_crop = crop.lower().strip()
    if normalized_crop not in SUPPORTED_CROPS:
        raise ValueError(f"Crop '{crop}' is not supported for price forecasting. Supported crops: {', '.join(c.title() for c in SUPPORTED_CROPS)}.")

    today = datetime.now(timezone.utc).date()
    history = [
        {"date": (today - timedelta(days=i)).isoformat(), "price": round(2100 + i * 5.2, 2)}
        for i in range(30, 0, -1)
    ]
    last_price = history[-1]["price"]

    forecast = [
        {
            "date": (today + timedelta(days=i)).isoformat(),
            "predicted_price": round(last_price + i * 8.5, 2),
            "naive_baseline": last_price,
        }
        for i in range(1, 8)
    ]

    return {
        "crop": normalized_crop.title(),
        "unit": "INR per Quintal",
        "historical": history,
        "forecast": forecast,
        "baseline_comparison": {
            "model_type": "LSTM",
            "model_mae": 32.5,
            "naive_mae": 48.0,
            "beats_baseline": True,
        },
        "is_stub": True,
    }
