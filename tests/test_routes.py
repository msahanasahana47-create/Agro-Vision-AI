import json


def test_auth_and_prediction_history_flow(client):
    """Test user registration, authenticated prediction, and history retrieval."""
    # 1. Register user
    reg_resp = client.post(
        "/register",
        data={"name": "Suresh Patel", "email": "suresh@example.com", "password": "SecurePassword123", "language": "hi"},
        headers={"Accept": "application/json"},
    )
    assert reg_resp.status_code == 201

    # 2. Make authenticated yield prediction
    yield_resp = client.post(
        "/api/yield",
        json={
            "crop": "rice", "rainfall": 250.0, "temperature": 27.0,
            "humidity": 85.0, "soil_ph": 6.8, "nitrogen": 100.0,
            "phosphorus": 50.0, "potassium": 50.0, "area": 3.0,
        },
    )
    assert yield_resp.status_code == 200

    # 3. Retrieve prediction history
    hist_resp = client.get("/api/history")
    assert hist_resp.status_code == 200
    hist_data = hist_resp.get_json()
    assert len(hist_data["predictions"]) == 1
    assert hist_data["predictions"][0]["module"] == "yield"

    # 4. Delete prediction entry
    pred_id = hist_data["predictions"][0]["id"]
    del_resp = client.delete(f"/api/history/{pred_id}")
    assert del_resp.status_code == 200


def test_invalid_yield_input_returns_400_or_422(client):
    """Test yield endpoint properly validates input types and bounds."""
    # Missing required field
    resp = client.post("/api/yield", json={"crop": "rice"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()

    # Out of bounds value
    resp_bounds = client.post(
        "/api/yield",
        json={
            "crop": "rice", "rainfall": 99999.0, "temperature": 27.0,
            "humidity": 85.0, "soil_ph": 6.8, "nitrogen": 100.0,
            "phosphorus": 50.0, "potassium": 50.0, "area": 3.0,
        },
    )
    assert resp_bounds.status_code == 422
    assert "error" in resp_bounds.get_json()


def test_price_api_unsupported_crop(client):
    """Test price endpoint error handling on unsupported crop."""
    resp = client.post("/api/price", json={"crop": "kiwi"})
    assert resp.status_code == 422
    assert "error" in resp.get_json()
