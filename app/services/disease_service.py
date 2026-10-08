"""Disease detection service using trained MobileNetV2 model."""
import os
from pathlib import Path
from typing import Dict, Any

import cv2
import numpy as np
from app.services.treatments import get_treatment_advice, DISCLAIMER

# Global model reference
_model = None
_class_names = ["Diseased", "Healthy"]   # fallback; overwritten by init
IMG_SIZE = (224, 224)


def init_disease_model(artifacts_dir: Path) -> None:
    """Load the trained Keras model at app startup."""
    global _model, _class_names

    # Model lives in ml/ (one level up from app/ml_artifacts)
    ml_dir = Path(__file__).parent.parent.parent / "ml"
    model_path   = ml_dir / "plant_disease_model.keras"
    classes_path = ml_dir / "classes.json"

    if not model_path.exists():
        print(f"[disease_service] WARNING: No trained model found at {model_path}. "
              "Using OpenCV fallback. Run ml/train_disease.py to train.")
        _model = None
        return

    try:
        import tensorflow as tf
        import json
        _model = tf.keras.models.load_model(str(model_path))
        if classes_path.exists():
            with open(classes_path) as f:
                _class_names = json.load(f)
        print(f"[disease_service] Loaded model from {model_path}, classes={_class_names}")
    except Exception as e:
        print(f"[disease_service] ERROR loading model: {e}. Using OpenCV fallback.")
        _model = None


def _predict_with_model(image_path: str) -> Dict[str, Any]:
    """Run inference using the trained Keras model."""
    import tensorflow as tf

    img = tf.keras.utils.load_img(image_path, target_size=IMG_SIZE)
    arr = tf.keras.utils.img_to_array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)

    preds = _model.predict(arr, verbose=0)[0]          # shape: (num_classes,)
    top_idx = int(np.argmax(preds))
    top_class = _class_names[top_idx]
    confidence = float(preds[top_idx])

    is_healthy  = top_class.lower() == "healthy"
    verdict     = "Healthy Leaf" if is_healthy else "Diseased Leaf"

    healthy_pct  = float(preds[_class_names.index("Healthy")] * 100) if "Healthy" in _class_names else (100.0 if is_healthy else 0.0)
    disease_pct  = float(preds[_class_names.index("Diseased")] * 100) if "Diseased" in _class_names else (0.0 if is_healthy else 100.0)

    uncertain = confidence < 0.60

    return {
        "predictions": [
            {"class": verdict, "confidence": confidence, "raw_class": top_class.lower()}
        ],
        "uncertain": uncertain,
        "uncertain_message": "Confidence is low. Please retake the photo in better lighting." if uncertain else None,
        "heatmap_url": None,
        "treatment": get_treatment_advice("healthy" if is_healthy else "diseased"),
        "disclaimer": DISCLAIMER,
        "healthy_percentage": round(healthy_pct, 1),
        "disease_percentage": round(disease_pct, 1),
    }


def _predict_with_opencv(image_path: str) -> Dict[str, Any]:
    """Fallback: color segmentation when no trained model is available."""
    img = cv2.imread(image_path)
    if img is None:
        return {
            "predictions": [{"class": "Error loading image", "confidence": 1.0}],
            "uncertain": True,
            "uncertain_message": "Could not read the image.",
            "heatmap_url": None,
            "treatment": get_treatment_advice("healthy"),
            "disclaimer": DISCLAIMER,
            "healthy_percentage": 0.0,
            "disease_percentage": 0.0,
        }

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_leaf = np.array([0, 25, 25])
    upper_leaf = np.array([179, 255, 255])
    leaf_mask  = cv2.inRange(hsv, lower_leaf, upper_leaf)

    lower_green = np.array([33, 25, 25])
    upper_green = np.array([85, 255, 255])
    green_mask  = cv2.inRange(hsv, lower_green, upper_green)

    healthy_mask  = cv2.bitwise_and(leaf_mask, green_mask)
    disease_mask  = cv2.bitwise_xor(leaf_mask, healthy_mask)

    healthy_pixels = cv2.countNonZero(healthy_mask)
    disease_pixels = cv2.countNonZero(disease_mask)
    total_leaf_pixels = healthy_pixels + disease_pixels

    if total_leaf_pixels > 0:
        healthy_pct = healthy_pixels / total_leaf_pixels
        disease_pct = disease_pixels / total_leaf_pixels
    else:
        healthy_pct = disease_pct = 0.0

    if total_leaf_pixels == 0:
        top_class, confidence = "No leaf detected", 1.0
    elif disease_pct > healthy_pct:
        top_class, confidence = "Diseased Leaf", disease_pct
    else:
        top_class, confidence = "Healthy Leaf", healthy_pct

    return {
        "predictions": [
            {"class": top_class, "confidence": float(confidence), "raw_class": "healthy" if "Healthy" in top_class else "diseased"}
        ],
        "uncertain": total_leaf_pixels < 1000,
        "uncertain_message": "Very small leaf area detected. Please retake the photo." if total_leaf_pixels < 1000 else None,
        "heatmap_url": None,
        "treatment": get_treatment_advice("healthy" if "Healthy" in top_class else "diseased"),
        "disclaimer": DISCLAIMER,
        "healthy_percentage": round(healthy_pct * 100, 1),
        "disease_percentage": round(disease_pct * 100, 1),
    }


def predict_disease(image_path: str, threshold: float = 0.60) -> Dict[str, Any]:
    """Predict whether a leaf is healthy or diseased."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    if _model is not None:
        return _predict_with_model(image_path)
    else:
        return _predict_with_opencv(image_path)
