<h1 align="center">🌿 Agro-Vision AI</h1>

<p align="center">
  <b>Multimodal Crop Intelligence &amp; Yield Optimization Platform</b><br/>
  AI-powered decision support for farmers — disease detection, yield prediction, crop recommendation &amp; price forecasting.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white"/>
  <img src="https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white"/>
  <img src="https://img.shields.io/badge/MobileNetV2-Transfer%20Learning-34A853?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Accuracy-99.73%25-brightgreen?style=for-the-badge"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square"/>
  <img src="https://img.shields.io/badge/Platform-Web%20%7C%20Mobile--First-orange?style=flat-square"/>
</p>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Model Performance](#-model-performance)
- [Getting Started](#-getting-started)
- [Dataset Preparation](#-dataset-preparation)
- [Running Tests](#-running-tests)
- [Contributing](#-contributing)

---

## 🌾 Overview

**Agro-Vision AI** is a production-grade, multimodal AI platform designed to empower farmers with intelligent, data-driven crop management tools. It combines deep learning computer vision, classical machine learning, and time-series forecasting into a unified, mobile-first web application.

The platform addresses critical agricultural challenges:
- 🍃 Early detection of plant diseases from leaf photographs
- 📈 Harvest yield estimation based on soil and climate data
- 🌱 Crop selection recommendations tailored to local conditions
- 💰 Wholesale (Mandi) price forecasting to maximize farm revenue

---

## ✨ Key Features

| Module | Description |
|--------|-------------|
| 🔬 **Disease Detection** | MobileNetV2 CNN with transfer learning — confidence scoring, uncertainty guardrails & Grad-CAM heatmaps |
| 📊 **Yield Prediction** | Sklearn pipelines (Linear Regression, Random Forest, XGBoost) using NPK, climate & acreage |
| 🌾 **Crop Recommendation** | Multi-class classification delivering top-3 crop suggestions with calibrated probabilities |
| 📉 **Price Forecasting** | Multi-step recursive LSTM networks for 7-day Mandi price predictions |
| 🧠 **Cross-Module Advisor** | Unified intelligence: crop suitability + yield + price forecast + estimated revenue |
| 🔐 **User Accounts** | Secure registration & authentication (Werkzeug) with per-user prediction history |
| 📱 **Mobile-First UI** | 360px viewport support, large tap targets, client-side image compression (~1024px) |
| 🌐 **Localization (i18n)** | Dynamic English ↔ Hindi switching via client-side JavaScript |
| 📋 **Model Registry** | Transparent model info page with metrics, training timestamps & dataset provenance |

---

## 🛠 Tech Stack

**Backend**
- Python 3.11+, Flask 3.x
- TensorFlow / Keras (MobileNetV2, LSTM)
- Scikit-learn, XGBoost
- SQLAlchemy, Flask-WTF (CSRF)
- Werkzeug (auth), Pillow (image processing)

**Frontend**
- Bootstrap 5 (mobile-first)
- Vanilla JavaScript (i18n, canvas compression)
- Jinja2 templates

**ML & Data**
- PlantVillage Dataset (disease detection)
- Transfer Learning: ImageNet → PlantVillage
- Two-phase fine-tuning (frozen base → unfrozen last 30 layers)

---

## 📁 Project Structure

```
Agro-Vision-AI/
├── app/
│   ├── __init__.py              # Flask application factory
│   ├── extensions.py            # SQLAlchemy, CSRF initialization
│   ├── models_db.py             # User & Prediction ORM schemas
│   ├── blueprints/              # Route handlers
│   │   ├── auth.py              # Registration & login
│   │   ├── disease.py           # Disease detection endpoint
│   │   ├── yield_.py            # Yield prediction endpoint
│   │   ├── recommend.py         # Crop recommendation endpoint
│   │   ├── price.py             # Price forecasting endpoint
│   │   ├── advisor.py           # Cross-module advisor
│   │   ├── history.py           # User prediction history
│   │   └── info.py              # Model registry page
│   ├── services/                # ML inference pipelines
│   │   ├── disease_service.py
│   │   ├── yield_service.py
│   │   ├── recommend_service.py
│   │   └── price_service.py
│   ├── templates/               # Jinja2 HTML templates
│   ├── static/                  # CSS, JS, i18n JSON, uploads/
│   └── ml_artifacts/            # Serialized models & metrics
├── ml/
│   ├── data/                    # raw/ & processed/ (gitignored)
│   ├── train_disease.py         # MobileNetV2 CNN training
│   ├── train_yield.py           # Yield regressor training
│   ├── train_recommend.py       # Crop recommender training
│   └── train_price.py           # LSTM price forecasting training
├── tests/                       # Pytest unit & integration suite
├── docs/                        # Architecture diagrams & screenshots
├── config.py                    # App configuration
├── requirements.txt             # Pinned Python dependencies
└── .env.example                 # Environment variable template
```

---

## 📊 Model Performance

### Disease Detection — MobileNetV2 Binary Classifier

| Metric | Value |
|--------|-------|
| ✅ Validation Accuracy | **99.73%** |
| ✅ Validation Loss | **0.0099** |
| 🏗️ Architecture | MobileNetV2 + Custom Classification Head |
| 📦 Dataset | PlantVillage (Healthy vs. Diseased) |
| ⚙️ Training Strategy | Two-phase transfer learning |

> **Uncertainty Guardrail:** Predictions with confidence < 60% are flagged as *"Uncertain"* to prevent confident misclassifications.

---

## 🚀 Getting Started

### Prerequisites
- Python **3.11** or **3.12**
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/msahanasahana47-create/Agro-Vision-AI.git
cd Agro-Vision-AI
```

### 2. Create & Activate Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```
Edit `.env` with your secret key, database URI, and other settings.

### 5. Run the Application
```bash
flask run --host=0.0.0.0 --port=5000
```
Open your browser at **http://localhost:5000**

---

## 📦 Dataset Preparation

Place raw data files in `ml/data/raw/` before training:

| File / Folder | Module | Description |
|---|---|---|
| `PlantVillage/` | Disease Detection | Leaf disease image dataset |
| `Crop_recommendation.csv` | Crop Recommendation | Soil nutrients, climate & crop labels |
| `crop_yield.csv` | Yield Prediction | Soil, climate, acreage & yield records |
| `mandi_prices.csv` | Price Forecasting | Date, crop name & modal wholesale prices |

> Raw datasets are excluded from version control via `.gitignore`.

---

## 🧪 Running Tests

```bash
pytest -v tests/
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**.

---

<p align="center">Built with ❤️ for farmers — Agro-Vision AI</p>

