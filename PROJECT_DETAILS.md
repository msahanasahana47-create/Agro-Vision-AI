# Agro-Vision AI - Detailed Project Report

## 1. Project Overview
**Agro-Vision AI** is a comprehensive, multimodal decision-support platform designed for farmers and agricultural stakeholders. It integrates deep learning for computer vision, machine learning for tabular data, and time-series forecasting to provide actionable insights. The application is built with a mobile-first approach, ensuring accessibility and ease of use in the field.

## 2. System Architecture & Structure
The project is structured to separate the web application (Flask) from the machine learning pipelines, ensuring modularity and maintainability.

```text
agrovision/
├── app/                        # Web Application (Flask)
│   ├── __init__.py             # Flask app factory and initialization
│   ├── blueprints/             # Route handlers (auth, disease, yield, recommend, price, advisor)
│   ├── services/               # Business logic and ML inference pipelines (e.g., disease_service.py)
│   ├── models_db.py            # Database schemas (SQLAlchemy)
│   ├── static/                 # CSS, JavaScript (client-side logic), and localization files
│   └── templates/              # Jinja2 HTML templates
├── ml/                         # Machine Learning Pipeline
│   ├── data/raw/dataset/Plant/ # Raw image dataset for training
│   ├── train_disease.py        # Training script for the Disease Detection model
│   ├── plant_disease_model.keras # Saved trained model
│   ├── classes.json            # Class label mapping
│   └── training_metrics.json   # Log of training performance
├── tests/                      # Pytest suite for unit and integration testing
├── README.md                   # Setup and quickstart guide
└── requirements.txt            # Python dependencies
```

## 3. How the Application Works
### Frontend
- **Mobile-First UI:** Built using Bootstrap 5, optimized for small screens (360px viewport support) with large tap targets.
- **Client-Side Optimization:** Images uploaded for disease scanning are compressed client-side (to ~1024px) using HTML5 Canvas before being sent to the server. This saves bandwidth and speeds up inference.
- **Localization (i18n):** Dynamic switching between English and Hindi using client-side JavaScript.

### Backend
- **Flask Framework:** Handles routing, API requests, and serves HTML templates.
- **Inference Services:** The `app/services/` directory contains the logic that bridges the web API and the ML models. For example, `disease_service.py` handles loading the `.keras` model and running predictions on uploaded images.

## 4. Machine Learning Models Used
The platform envisions multiple ML modules, but let's detail the current state, especially what was manually trained.

### A. Disease Detection (Manually Trained)
This is the core computer vision component that we manually trained using a custom dataset.

- **Task:** Binary Classification (Healthy vs. Diseased leaf).
- **Architecture:** **MobileNetV2** (Transfer Learning). MobileNetV2 was chosen for its excellent trade-off between accuracy and computational efficiency, making it ideal for web and mobile deployments.
- **Training Strategy:** 
  - **Phase 1 (Head Only):** The base MobileNetV2 layers (pre-trained on ImageNet) were frozen. A new classification head (GlobalAveragePooling -> Dropout -> Dense -> Dropout -> Softmax) was added and trained for 10 epochs.
  - **Phase 2 (Fine-Tuning):** The last 30 layers of the base MobileNetV2 model were unfrozen and fine-tuned with a lower learning rate for another 10 epochs to adapt specifically to leaf features.
- **Dataset:** The model was trained on a subset of the renowned **PlantVillage dataset**. The raw images were placed locally in `ml/data/raw/dataset/Plant/`. To create a binary classifier, folders ending in `_healthy` (e.g., `Tomato_healthy`, `Pepper__bell___healthy`) were grouped into the "Healthy" class, while all other folders (e.g., `Tomato_Early_blight_disease`) were grouped into the "Diseased" class.
- **Performance:** 
  - **Validation Accuracy: 99.73%**
  - **Validation Loss: 0.0099**
- **Inference Pipeline:** When an image is uploaded, `disease_service.py` preprocesses the image (resizing to 224x224 and scaling), passes it through the loaded `plant_disease_model.keras`, and extracts the confidence score. It also includes an "uncertainty" guardrail (if confidence < 60%) to prevent confident misclassifications.
- **Fallback:** If the Keras model is not found, the system gracefully falls back to an OpenCV-based color segmentation method to estimate the percentage of healthy (green) vs. diseased (non-green) tissue.

### B. Other Planned Modules (F2-F5)
*(Note: These modules are part of the platform's architecture but require their respective datasets to be placed and trained similar to the disease model).*
- **Yield Prediction:** Sklearn regression pipelines (Random Forest, XGBoost) using soil nutrients and climate data.
- **Crop Recommendation:** Multi-class classification for suggesting the best crop based on soil and weather.
- **Mandi Price Forecasting:** LSTM neural networks for time-series forecasting of crop prices.
- **Cross-Module Advisor:** A unified pipeline aggregating predictions from all modules to give a comprehensive farm intelligence report (estimated revenue, crop suitability, etc.).

## 5. Summary of Manual Interventions
1. **Dataset Organization:** Structured the raw image data into class-specific folders.
2. **Training Script Creation:** Wrote `ml/train_disease.py` to handle data loading, augmentation, and the two-phase transfer learning process using TensorFlow/Keras.
3. **Model Training:** Executed the training script, which achieved a highly accurate model (99.73%) and saved the artifacts (`.keras` model, `classes.json`, `training_metrics.json`).
4. **Service Integration:** Updated `disease_service.py` to seamlessly load the trained model at Flask application startup and use it for real-time inference via the `/api/disease` endpoint.
5. **UI Refinement:** Updated `main.js` to parse the new binary prediction format and display a clean, single verdict badge (✅ Healthy or ⚠️ Diseased) along with the confidence percentage.
