"""Crop recommendation service based on soil and climatic features."""
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


# Each crop: (opt_N, opt_P, opt_K, opt_temp, opt_humidity, opt_ph, opt_rainfall)
# Values represent the centre of the ideal range for each feature
_CROP_OPTIMA = {
    "Rice":      (80,  40,  40,  25, 80, 6.0, 200),
    "Maize":     (90,  45,  45,  22, 65, 6.0, 120),
    "Wheat":     (100, 50,  50,  20, 55, 6.5, 100),
    "Chickpea":  (40,  60,  80,  18, 45, 7.0,  70),
    "Kidneybeans":(20, 60,  20,  20, 60, 5.5,  90),
    "Pigeonpeas":(20,  60,  20,  28, 60, 6.5, 120),
    "Mothbeans": (21,  48,  24,  28, 50, 7.0,  50),
    "Mungbean":  (20,  40,  20,  28, 65, 6.5,  80),
    "Blackgram": (40,  67,  19,  29, 65, 6.5, 100),
    "Lentil":    (19,  67,  19,  18, 50, 6.5,  45),
    "Pomegranate":(18, 18,  20,  22, 90, 6.0, 110),
    "Banana":    (100, 75, 50,  27, 80, 6.0, 100),
    "Mango":     (20,  20,  30,  30, 70, 5.8, 100),
    "Grapes":    (20,  150, 200, 23, 80, 6.0,  90),
    "Watermelon":(100, 10,  50,  26, 85, 6.5, 100),
    "Muskmelon": (100, 10,  50,  28, 85, 6.5,  80),
    "Apple":     (21,  134, 199, 22, 92, 5.5, 114),
    "Orange":    (20,  10,  10,  23, 92, 7.0, 110),
    "Papaya":    (50,  50,  50,  34, 92, 7.0, 150),
    "Coconut":   (22,  16,  30,  27, 94, 5.5, 175),
    "Cotton":    (118, 46,  20,  25, 80, 7.0, 100),
    "Jute":      (78,  46,  40,  25, 80, 6.5, 175),
    "Coffee":    (101, 28,  29,  25, 58, 6.8, 150),
}


def _score_crop(
    crop_optima: tuple,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
) -> float:
    """Compute a 0–1 suitability score for a crop given input conditions."""
    opt_n, opt_p, opt_k, opt_t, opt_h, opt_ph, opt_r = crop_optima
    scores = [
        max(0.0, 1 - abs(nitrogen - opt_n) / 150),
        max(0.0, 1 - abs(phosphorus - opt_p) / 150),
        max(0.0, 1 - abs(potassium - opt_k) / 150),
        max(0.0, 1 - abs(temperature - opt_t) / 25),
        max(0.0, 1 - abs(humidity - opt_h) / 60),
        max(0.0, 1 - abs(ph - opt_ph) / 4),
        max(0.0, 1 - abs(rainfall - opt_r) / 300),
    ]
    return sum(scores) / len(scores)


def recommend_crop(
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
) -> Dict[str, Any]:
    """Return top-3 crop recommendations with calibrated suitability scores."""
    validate_recommend_inputs(
        nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall
    )

    if _RECOMMEND_PIPELINE is None:
        # Score every crop against the input conditions
        ranked = []
        for crop, optima in _CROP_OPTIMA.items():
            score = _score_crop(optima, nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall)
            ranked.append((crop, score))

        ranked.sort(key=lambda x: x[1], reverse=True)
        top3 = ranked[:3]

        # Normalise top-3 scores so they sum to 1.0 (probabilities)
        total = sum(s for _, s in top3) or 1.0
        top_crops = [
            {"crop": crop, "probability": round(score / total, 2)}
            for crop, score in top3
        ]

        return {"top_crops": top_crops, "is_stub": True}

    # Real model inference (implemented in M4)
    return {}
