"""Crop yield prediction service."""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import joblib

_YIELD_PIPELINE = None


def init_yield_model(artifacts_dir: Path) -> None:
    """Load yield pipeline once at app startup."""
    global _YIELD_PIPELINE
    pipeline_path = artifacts_dir / "yield" / "pipeline.joblib"
    if pipeline_path.exists():
        _YIELD_PIPELINE = joblib.load(pipeline_path)


def validate_yield_inputs(
    crop: str,
    rainfall: float,
    temperature: float,
    humidity: float,
    soil_ph: float,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    area: float,
) -> None:
    """Validate numerical and categorical yield prediction inputs."""
    if not crop or not isinstance(crop, str) or not crop.strip():
        raise ValueError("Crop name is required and cannot be empty.")
    if rainfall < 0 or rainfall > 3500:
        raise ValueError("Rainfall must be between 0 and 3500 mm.")
    if temperature < -10 or temperature > 60:
        raise ValueError("Temperature must be between -10°C and 60°C.")
    if humidity < 0 or humidity > 100:
        raise ValueError("Humidity must be between 0% and 100%.")
    if soil_ph < 0 or soil_ph > 14:
        raise ValueError("Soil pH must be between 0 and 14.")
    if nitrogen < 0 or nitrogen > 500:
        raise ValueError("Nitrogen (N) must be between 0 and 500 kg/ha.")
    if phosphorus < 0 or phosphorus > 500:
        raise ValueError("Phosphorus (P) must be between 0 and 500 kg/ha.")
    if potassium < 0 or potassium > 500:
        raise ValueError("Potassium (K) must be between 0 and 500 kg/ha.")
    if area <= 0 or area > 100000:
        raise ValueError("Cultivation area must be greater than 0 and less than 100,000 hectares.")


def predict_yield(
    crop: str,
    rainfall: float,
    temperature: float,
    humidity: float,
    soil_ph: float,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    area: float,
) -> Dict[str, Any]:
    """Predict crop yield and return top feature importances."""
    validate_yield_inputs(
        crop, rainfall, temperature, humidity, soil_ph, nitrogen, phosphorus, potassium, area
    )

    if _YIELD_PIPELINE is None:
        # Stub response for scaffolding phase
        estimated_yield = round(3.5 * area, 2)
        return {
            "predicted_yield": estimated_yield,
            "yield_per_hectare": 3.5,
            "unit": "metric tons",
            "top_features": [
                {"feature": "Rainfall", "importance": 0.35},
                {"feature": "Nitrogen", "importance": 0.25},
                {"feature": "Temperature", "importance": 0.20},
                {"feature": "Phosphorus", "importance": 0.12},
                {"feature": "Soil pH", "importance": 0.08},
            ],
            "is_stub": True,
        }

    # Model inference logic will run here (implemented in M3)
    return {}
