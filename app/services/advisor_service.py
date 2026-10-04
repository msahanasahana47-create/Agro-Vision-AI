"""Cross-module crop intelligence and yield optimization advisor service."""
from typing import Dict, Any, List, Optional
from app.services.recommend_service import recommend_crop
from app.services.yield_service import predict_yield
from app.services.price_service import forecast_price

# Configurable heuristic disease yield penalty (e.g. 15% estimated loss if foliar disease detected)
DEFAULT_DISEASE_YIELD_LOSS_HEURISTIC_PERCENT = 15.0


def run_cross_module_advisor(
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
    area: float,
    has_disease_risk: bool = False,
    disease_name: Optional[str] = None,
    disease_loss_penalty_percent: float = DEFAULT_DISEASE_YIELD_LOSS_HEURISTIC_PERCENT,
) -> Dict[str, Any]:
    """Execute integrated workflow: recommend crops -> predict yield -> forecast price -> estimate revenue."""
    # 1. Step 1: Crop recommendation
    rec_result = recommend_crop(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall)
    candidate_crops = rec_result.get("top_crops", [])

    candidates_analysis = []
    for cand in candidate_crops:
        crop_name = cand["crop"]
        probability = cand["probability"]

        # 2. Step 2: Yield prediction for candidate crop
        yield_res = predict_yield(
            crop=crop_name,
            rainfall=rainfall,
            temperature=temperature,
            humidity=humidity,
            soil_ph=ph,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            area=area,
        )
        base_yield = yield_res["predicted_yield"]  # metric tons

        # Disease heuristic adjustment (Clearly labeled heuristic, NOT a model output)
        adjusted_yield = base_yield
        heuristic_loss_applied = 0.0
        if has_disease_risk:
            heuristic_loss_applied = round(base_yield * (disease_loss_penalty_percent / 100.0), 2)
            adjusted_yield = round(base_yield - heuristic_loss_applied, 2)

        # 3. Step 3: Price forecast
        price_per_ton = 25000.0  # fallback ~2500 INR/quintal = 25000 INR/ton
        price_note = "Standard market projection"
        try:
            price_res = forecast_price(crop_name)
            # 1 Quintal = 100 kg = 0.1 ton; 1 ton = 10 quintals
            avg_forecast_quintal = sum(f["predicted_price"] for f in price_res["forecast"]) / len(price_res["forecast"])
            price_per_ton = round(avg_forecast_quintal * 10, 2)
            price_note = f"7-day average forecast from Mandi time-series ({avg_forecast_quintal:.1f} INR/quintal)"
        except Exception:
            pass

        # 4. Step 4: Revenue calculation
        est_gross_revenue = round(adjusted_yield * price_per_ton, 2)

        candidates_analysis.append({
            "crop": crop_name,
            "suitability_probability": probability,
            "base_yield_tons": base_yield,
            "adjusted_yield_tons": adjusted_yield,
            "projected_price_per_ton_inr": price_per_ton,
            "projected_revenue_inr": est_gross_revenue,
            "price_outlook_note": price_note,
        })

    disease_risk_note = None
    if has_disease_risk:
        disease_risk_note = {
            "is_advisory_heuristic": True,
            "label": "Configurable Agronomic Heuristic (NOT an ML model output)",
            "disease_detected": disease_name or "Detected Foliar Infection",
            "penalty_percentage": disease_loss_penalty_percent,
            "disclaimer": "Advisory only. Consult a local agricultural officer for certified field inspection.",
        }

    return {
        "area_hectares": area,
        "soil_climate_summary": {
            "N": nitrogen, "P": phosphorus, "K": potassium,
            "temperature": temperature, "humidity": humidity,
            "ph": ph, "rainfall": rainfall,
        },
        "candidates": candidates_analysis,
        "disease_risk_note": disease_risk_note,
        "is_stub": any(cand.get("suitability_probability") for cand in candidate_crops) is not None,
    }
