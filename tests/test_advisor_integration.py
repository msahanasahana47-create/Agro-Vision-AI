def test_api_advisor_valid_flow(client):
    """Test full advisor flow returns candidate crops, yield, price, and projected revenue."""
    payload = {
        "nitrogen": 85.0,
        "phosphorus": 45.0,
        "potassium": 40.0,
        "temperature": 26.5,
        "humidity": 78.0,
        "ph": 6.8,
        "rainfall": 195.0,
        "area": 2.0,
        "has_disease_risk": False,
    }
    response = client.post("/api/advisor", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "candidates" in data
    assert len(data["candidates"]) > 0

    candidate = data["candidates"][0]
    assert "crop" in candidate
    assert "base_yield_tons" in candidate
    assert "adjusted_yield_tons" in candidate
    assert "projected_price_per_ton_inr" in candidate
    assert "projected_revenue_inr" in candidate
    assert candidate["projected_revenue_inr"] > 0
    assert data["disease_risk_note"] is None


def test_api_advisor_with_disease_risk_heuristic(client):
    """Test advisor flow applies the labeled heuristic yield loss when disease risk is checked."""
    payload = {
        "nitrogen": 85.0,
        "phosphorus": 45.0,
        "potassium": 40.0,
        "temperature": 26.5,
        "humidity": 78.0,
        "ph": 6.8,
        "rainfall": 195.0,
        "area": 2.0,
        "has_disease_risk": True,
        "disease_name": "Bacterial Blight",
    }
    response = client.post("/api/advisor", json=payload)
    assert response.status_code == 200
    data = response.get_json()

    assert data["disease_risk_note"] is not None
    assert data["disease_risk_note"]["is_advisory_heuristic"] is True
    assert "heuristic" in data["disease_risk_note"]["label"].lower()
    assert "consult a local agricultural officer" in data["disease_risk_note"]["disclaimer"].lower()

    # Verify that adjusted yield is lower than base yield due to the 15% heuristic
    candidate = data["candidates"][0]
    assert candidate["adjusted_yield_tons"] < candidate["base_yield_tons"]


def test_api_advisor_invalid_inputs(client):
    """Test advisor validation rejects invalid soil pH or area."""
    # Negative area
    resp1 = client.post("/api/advisor", json={
        "nitrogen": 85, "phosphorus": 45, "potassium": 40,
        "temperature": 26, "humidity": 78, "ph": 6.8, "rainfall": 195, "area": -1
    })
    assert resp1.status_code == 422

    # Out of bounds pH (> 14)
    resp2 = client.post("/api/advisor", json={
        "nitrogen": 85, "phosphorus": 45, "potassium": 40,
        "temperature": 26, "humidity": 78, "ph": 18.5, "rainfall": 195, "area": 1.0
    })
    assert resp2.status_code == 422
