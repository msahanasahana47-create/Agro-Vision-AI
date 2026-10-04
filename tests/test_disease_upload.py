import io
from PIL import Image


def create_dummy_image(format="PNG", size=(100, 100), color=(0, 255, 0)):
    """Create in-memory image bytes."""
    buf = io.BytesIO()
    img = Image.new("RGB", size, color=color)
    img.save(buf, format=format)
    buf.seek(0)
    return buf


def test_disease_valid_upload(client):
    """Test valid image upload returns top-3, confidence, and treatment advice."""
    img_buf = create_dummy_image(format="PNG")
    data = {
        "image": (img_buf, "leaf_sample.png")
    }
    response = client.post("/api/disease", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    res_data = response.get_json()
    assert "predictions" in res_data
    assert len(res_data["predictions"]) == 3
    assert "uncertain" in res_data
    assert "treatment" in res_data
    assert "disclaimer" in res_data
    assert "consult a local agricultural officer" in res_data["disclaimer"].lower()


def test_disease_disallowed_extension(client):
    """Test unsupported file extensions are rejected with HTTP 415."""
    buf = io.BytesIO(b"fake text content")
    data = {
        "image": (buf, "malicious.txt")
    }
    response = client.post("/api/disease", data=data, content_type="multipart/form-data")
    assert response.status_code == 415
    res_data = response.get_json()
    assert "Unsupported file format" in res_data["error"]


def test_disease_missing_file_key(client):
    """Test request without 'image' key returns HTTP 400."""
    response = client.post("/api/disease", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_disease_empty_filename(client):
    """Test uploading an empty filename returns HTTP 400."""
    buf = io.BytesIO(b"")
    data = {"image": (buf, "")}
    response = client.post("/api/disease", data=data, content_type="multipart/form-data")
    assert response.status_code == 400


def test_disease_oversized_file(client):
    """Test uploading file exceeding 5MB returns HTTP 413."""
    # 5MB + 10KB
    large_buf = io.BytesIO(b"0" * (5 * 1024 * 1024 + 10240))
    data = {"image": (large_buf, "large.jpg")}
    response = client.post("/api/disease", data=data, content_type="multipart/form-data")
    assert response.status_code == 413
    assert "exceeds" in response.get_json()["error"].lower()
