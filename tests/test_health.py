def test_health_endpoint(client):
    """Test the /health check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "agro-vision-ai"


def test_index_page(client):
    """Test that the index dashboard loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Agro-Vision AI" in response.data


def test_models_api(client):
    """Test model info endpoint returns model dictionary."""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.get_json()
    assert "disease" in data
    assert "yield" in data
    assert "recommend" in data
    assert "price" in data
