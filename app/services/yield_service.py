"""Crop yield prediction service."""
import math
from pathlib import Path
from typing import Dict, Any
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


def _heuristic_yield_per_ha(
    crop: str,
    rainfall: float,
    temperature: float,
    humidity: float,
    soil_ph: float,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
) -> float:
    """Agronomic heuristic: estimate yield per hectare (metric tons) from input values."""
    # Real-world average base yields by crop (t/ha)
    CROP_BASE = {
        "rice": 4.5, "wheat": 3.2, "maize": 5.0, "corn": 5.0,
        "jute": 2.5, "cotton": 1.8, "sugarcane": 70.0, "potato": 20.0,
        "tomato": 25.0, "onion": 18.0, "soybean": 2.8, "groundnut": 2.2,
        "barley": 2.8, "millet": 1.5, "sorghum": 2.0,
    }
    base = CROP_BASE.get(crop.lower().strip(), 3.5)

    # Nutrient sufficiency (optimal N≈100, P≈50, K≈50 kg/ha)
    n_score = max(0.0, 1 - abs(nitrogen - 100) / 200)
    p_score = max(0.0, 1 - abs(phosphorus - 50) / 150)
    k_score = max(0.0, 1 - abs(potassium - 50) / 150)
    nutrient_factor = 0.6 + 0.4 * (n_score * 0.5 + p_score * 0.25 + k_score * 0.25)

    # Rainfall (optimal 150–300 mm)
    rain_score = max(0.0, 1 - abs(rainfall - 225) / 400)
    rain_factor = 0.7 + 0.3 * rain_score

    # Temperature (optimal 20–30°C)
    temp_score = max(0.0, 1 - abs(temperature - 25) / 20)
    temp_factor = 0.7 + 0.3 * temp_score

    # Soil pH (optimal 5.5–7.0)
    ph_score = max(0.0, 1 - abs(soil_ph - 6.25) / 3)
    ph_factor = 0.75 + 0.25 * ph_score

    # Humidity (optimal 60–85%)
    hum_score = max(0.0, 1 - abs(humidity - 72) / 50)
    hum_factor = 0.8 + 0.2 * hum_score

    yield_ha = base * nutrient_factor * rain_factor * temp_factor * ph_factor * hum_factor
    return max(0.1, round(yield_ha, 2))


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
        yield_per_ha = _heuristic_yield_per_ha(
            crop, rainfall, temperature, humidity, soil_ph, nitrogen, phosphorus, potassium
        )
        total_yield = round(yield_per_ha * area, 2)

        # Feature importances: how much each input drives the result (higher = more limiting/boosting)
        n_imp    = max(0.05, 1 - abs(nitrogen - 100) / 200)
        rain_imp = max(0.05, 1 - abs(rainfall - 225) / 400)
        temp_imp = max(0.05, 1 - abs(temperature - 25) / 20)
        p_imp    = max(0.05, 1 - abs(phosphorus - 50) / 150)
        ph_imp   = max(0.05, 1 - abs(soil_ph - 6.25) / 3)
        total_imp = n_imp + rain_imp + temp_imp + p_imp + ph_imp
        features = sorted([
            {"feature": "Nitrogen",    "importance": round(n_imp / total_imp, 2)},
            {"feature": "Rainfall",    "importance": round(rain_imp / total_imp, 2)},
            {"feature": "Temperature", "importance": round(temp_imp / total_imp, 2)},
            {"feature": "Phosphorus",  "importance": round(p_imp / total_imp, 2)},
            {"feature": "Soil pH",     "importance": round(ph_imp / total_imp, 2)},
        ], key=lambda x: x["importance"], reverse=True)

        return {
            "predicted_yield": total_yield,
            "yield_per_hectare": yield_per_ha,
            "unit": "metric tons",
            "top_features": features,
            "is_stub": True,
        }

    # Real model inference (implemented in M3)
    return {}
