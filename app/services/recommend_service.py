"""Crop recommendation service based on soil and climatic features."""
import os
from pathlib import Path
from typing import Dict, Any, List
import joblib

_RECOMMEND_PIPELINE = None


def init_recommend_model(artifacts_dir: Path) -> None:
    """Load crop recommendation pipeline once at app startup."""
    global _RECOMMEND_PIPELINE
    pipeline_path = artifacts_dir / "recommend" / "pipeline.joblib"
    if pipeline_path.exists():
        _RECOMMEND_PIPELINE = joblib.load(pipeline_path)


def validate_recommend_inputs(
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
) -> None:
    """Validate numerical inputs for crop recommendation."""
    if nitrogen < 0 or nitrogen > 500:
        raise ValueError("Nitrogen (N) must be between 0 and 500 kg/ha.")
    if phosphorus < 0 or phosphorus > 500:
        raise ValueError("Phosphorus (P) must be between 0 and 500 kg/ha.")
    if potassium < 0 or potassium > 500:
        raise ValueError("Potassium (K) must be between 0 and 500 kg/ha.")
    if temperature < -10 or temperature > 60:
        raise ValueError("Temperature must be between -10°C and 60°C.")
    if humidity < 0 or humidity > 100:
        raise ValueError("Humidity must be between 0% and 100%.")
    if ph < 0 or ph > 14:
        raise ValueError("pH must be between 0 and 14.")
    if rainfall < 0 or rainfall > 3500:
        raise ValueError("Rainfall must be between 0 and 3500 mm.")


def recommend_crop(
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
) -> Dict[str, Any]:
    """Return top-3 crop recommendations with calibrated probabilities."""
    validate_recommend_inputs(
        nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall
    )

    if _RECOMMEND_PIPELINE is None:
        # Stub response for scaffolding phase
        return {
            "top_crops": [
                {"crop": "Rice", "probability": 0.65},
                {"crop": "Maize", "probability": 0.22},
                {"crop": "Jute", "probability": 0.13},
            ],
            "is_stub": True,
        }

    # Model inference logic will run here (implemented in M4)
    return {}
