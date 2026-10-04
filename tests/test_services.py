import pytest
from app.services.treatments import get_treatment_advice, DISCLAIMER
from app.services.disease_service import predict_disease
from app.services.yield_service import predict_yield, validate_yield_inputs
from app.services.recommend_service import recommend_crop, validate_recommend_inputs
from app.services.price_service import forecast_price, SUPPORTED_CROPS
from app.services.advisor_service import run_cross_module_advisor


def test_treatment_disclaimer_mandatory():
    """Verify that every treatment recommendation contains the mandatory disclaimer."""
    healthy_advice = get_treatment_advice("healthy")
    assert "disclaimer" in healthy_advice
    assert "consult a local agricultural officer" in healthy_advice["disclaimer"].lower()

    unknown_advice = get_treatment_advice("unknown_blight_xyz")
    assert "consult a local agricultural officer" in unknown_advice["disclaimer"].lower()


def test_yield_service_validation():
    """Verify input validation rules for crop yield prediction."""
    # Negative rainfall should raise ValueError
    with pytest.raises(ValueError, match="Rainfall"):
        validate_yield_inputs("rice", -5.0, 25.0, 80.0, 6.5, 90.0, 42.0, 43.0, 1.0)

    # Empty crop should raise ValueError
    with pytest.raises(ValueError, match="Crop name"):
        validate_yield_inputs("", 200.0, 25.0, 80.0, 6.5, 90.0, 42.0, 43.0, 1.0)

    # Negative area should raise ValueError
    with pytest.raises(ValueError, match="area"):
        validate_yield_inputs("rice", 200.0, 25.0, 80.0, 6.5, 90.0, 42.0, 43.0, -1.0)


def test_yield_service_prediction():
    """Verify yield prediction returns expected structure and feature importances."""
    res = predict_yield(
        crop="Rice",
        rainfall=200.0,
        temperature=26.0,
        humidity=80.0,
        soil_ph=6.5,
        nitrogen=90.0,
        phosphorus=42.0,
        potassium=43.0,
        area=2.0,
    )
    assert "predicted_yield" in res
    assert "top_features" in res
    assert len(res["top_features"]) > 0


def test_recommend_service():
    """Verify crop recommendation returns top crops with probabilities."""
    res = recommend_crop(
        nitrogen=90.0,
        phosphorus=42.0,
        potassium=43.0,
        temperature=25.0,
        humidity=82.0,
        ph=6.5,
        rainfall=200.0,
    )
    assert "top_crops" in res
    assert len(res["top_crops"]) == 3
    assert all("crop" in c and "probability" in c for c in res["top_crops"])


def test_price_service_supported_crops():
    """Verify 7-day forecast and baseline comparison for supported crop."""
    res = forecast_price("rice")
    assert res["crop"] == "Rice"
    assert len(res["forecast"]) == 7
    assert "baseline_comparison" in res
    assert "naive_baseline" in res["forecast"][0]


def test_price_service_unsupported_crop():
    """Verify that unsupported crop returns ValueError."""
    with pytest.raises(ValueError, match="not supported"):
        forecast_price("dragonfruit")


def test_cross_module_advisor_flow():
    """Verify the integrated advisor combines recommendation, yield, price, and heuristic note."""
    res = run_cross_module_advisor(
        nitrogen=90.0,
        phosphorus=42.0,
        potassium=43.0,
        temperature=25.0,
        humidity=80.0,
        ph=6.5,
        rainfall=200.0,
        area=2.5,
        has_disease_risk=True,
        disease_name="Early Blight",
    )
    assert "candidates" in res
    assert len(res["candidates"]) > 0
    candidate = res["candidates"][0]
    assert "adjusted_yield_tons" in candidate
    assert "projected_revenue_inr" in candidate
    assert res["disease_risk_note"] is not None
    assert res["disease_risk_note"]["is_advisory_heuristic"] is True
    assert "consult a local agricultural officer" in res["disease_risk_note"]["disclaimer"].lower()
