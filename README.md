# Agro-Vision AI: Multimodal Crop Intelligence & Yield Optimization

Agro-Vision AI is a production-grade multimodal decision support platform built for farmers. It combines deep learning computer vision, tabular machine learning, and time-series forecasting with an integrated agronomic advisor in a mobile-first interface.

---

## Features
- **F1 Disease Detection:** Deep CNN (MobileNetV2) transfer learning on leaf photography, delivering top-3 diagnosis, confidence scoring, "uncertain" out-of-distribution guardrails, Grad-CAM interpretability heatmaps, and advisory treatments.
- **F2 Yield Prediction:** Sklearn regression pipelines (Linear Regression, Random Forest, XGBoost) evaluating soil nutrients (NPK), climate, and acreage to predict total harvest in metric tons with feature importances.
- **F3 Crop Recommendation:** Multi-class classification pipeline determining top-3 crops suited to soil chemistry and microclimate conditions with calibrated probabilities.
- **F4 Mandi Price Forecasting:** Multi-step recursive LSTM neural networks providing 7-day ahead price forecasts against naive last-value and ARIMA baselines.
- **F5 Cross-Module Advisor:** Unified pipeline calculating crop suitability, projected yield, 7-day price expectations, estimated revenue ($Yield \times Price$), and clearly labeled advisory disease risk heuristics.
- **F6 User Accounts & History:** Secure registration and authentication (Werkzeug), storing per-user prediction logs with deletion capabilities.
- **F7 Mobile-First UI & i18n:** 360px viewport support, large tap targets, client-side canvas compression (~1024px), dynamic English and Hindi localization.
- **F8 Model Registry & Auditing:** Transparent model information page displaying metrics, training timestamps, dataset provenance, and version tracking.

---

## Project Structure
```
agrovision/
  .agent/rules/agrovision.md       # Non-negotiable architectural rules
  .agent/workflows/                # Automated ML & operational workflows
  app/
    __init__.py                    # Flask application factory
    extensions.py                  # SQLAlchemy, CSRF initialization
    models_db.py                   # User & Prediction ORM schemas
    blueprints/                    # Route handlers (auth, disease, yield, recommend, price, advisor, history, info)
    services/                      # Business logic & ML inference pipelines
    templates/                     # Mobile-first Jinja templates
    static/                        # CSS, JS (compression/i18n), i18n JSON files, uploads/
    ml_artifacts/                  # Serialized models, scalers, and metrics.json files
  ml/
    data/                          # raw/ (gitignored), processed/, field_test/
    notebooks/                     # Exploratory data analysis notebooks
    train_disease.py               # MobileNetV2 CNN training script
    train_yield.py                 # Yield regressor training script
    train_recommend.py             # Crop recommender training script
    train_price.py                 # LSTM price forecasting script
    evaluate.py                    # Independent evaluation & field test harness
  tests/                           # Pytest unit and integration test suite
  docs/                            # Architecture diagrams, results, and screenshots
```

---

## Local Setup

### 1. Prerequisites
- Python 3.11 or 3.12
- Git

### 2. Environment Setup
```bash
# Clone the repository
git clone <repo-url>
cd project

# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install pinned dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 4. Running Tests
```bash
pytest -v tests/
```

### 5. Running the Application
```bash
flask run --host=0.0.0.0 --port=5000
```
Open your browser at `http://localhost:5000`.

---

## Dataset Preparation (For M1–M5)
Place raw data files in `ml/data/raw/`:
- `PlantVillage/` or `rice_leaf_diseases/`: Directory of leaf disease images.
- `Crop_recommendation.csv`: Soil nutrients, climatic variables, and crop labels.
- `crop_yield.csv`: Soil, climate, acreage, and yield records.
- `mandi_prices.csv`: Date, crop name, and modal wholesale prices.
