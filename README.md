# 🛡️ Network Anomaly Detection System

A real-time network intrusion detection system using a **weighted ensemble of XGBoost, Isolation Forest, and Autoencoder** models, served via a FastAPI REST API and visualized through a Streamlit dashboard.

---

## 🚀 Quick Start (Deploy Everything)

```bash
# Make the deploy script executable & run it
chmod +x deploy.sh
./deploy.sh
```

| Service | URL |
|---------|-----|
| Streamlit Dashboard | http://localhost:8501 |
| FastAPI Backend | http://localhost:8000 |
| Interactive API Docs | http://localhost:8000/docs |

**Stop all services:**
```bash
./deploy.sh --stop
# or
make stop
```

---

## 📁 Project Structure

```
network-anomaly-detection/
├── data/                    # Dataset files
│   ├── combinenew.csv       # Raw CIC-IDS-2017 dataset
│   ├── X_scaled.csv         # Preprocessed features
│   └── y.csv                # Encoded labels
├── training/                # Model training scripts
│   ├── preprocess.py        # Data cleaning & feature scaling
│   ├── train_xgb.py         # XGBoost classifier
│   ├── train_iso.py         # Isolation Forest
│   ├── train_autoencoder.py # Autoencoder (TensorFlow/Keras)
│   └── evaluate.py          # Metrics, ROC, cross-validation
├── models/                  # Saved trained models
│   ├── xgb_model.pkl
│   ├── iso_model.pkl
│   ├── autoencoder.h5
│   └── scaler.pkl
├── backend/
│   ├── main.py              # FastAPI app + /predict endpoint
│   └── predict.py           # Full 3-model ensemble logic
├── dashboard/
│   └── app.py               # Streamlit web UI
├── api_env/                 # venv: FastAPI + Streamlit
├── ml_env/                  # venv: scikit-learn + TensorFlow
├── deploy.sh                # ← One-command deploy
├── Makefile                 # ← Convenience commands
├── requirements-api.txt     # API environment dependencies
└── requirements-ml.txt      # ML environment dependencies
```

---

## ⚙️ Make Commands

```bash
make deploy      # Start API + Dashboard
make stop        # Stop all services
make api         # Start only FastAPI (with --reload)
make dashboard   # Start only Streamlit
make train       # Train all 3 models (ml_env)
make preprocess  # Run data preprocessing (ml_env)
make evaluate    # Run model evaluation (ml_env)
make predict     # Quick curl test prediction
make logs-api    # Tail API server log
make logs-dash   # Tail dashboard log
make help        # Show all commands
```

---

## 🔬 How It Works

### Ensemble Detection

```
final_score = 0.4 × XGBoost + 0.3 × Isolation Forest + 0.3 × Autoencoder

prediction  = "Attack" if final_score > 0.5 else "Normal"
```

| Model | Type | Role |
|-------|------|------|
| XGBoost | Supervised | Learns known attack signatures |
| Isolation Forest | Unsupervised | Detects novel anomalies |
| Autoencoder | Deep Learning | Reconstruction error on abnormal traffic |

### Input Features

| Feature | Description |
|---------|-------------|
| `Flow Duration` | Duration of the network flow (µs) |
| `Total Fwd Packets` | Packets in forward direction |
| `Total Backward Packets` | Packets in backward direction |
| `Total Length of Fwd Packets` | Byte size of forward packets |

### API Predict Endpoint

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Flow_Duration": 1000,
    "Total_Fwd_Packets": 10,
    "Total_Backward_Packets": 5,
    "Total_Length_of_Fwd_Packets": 500
  }'
```

**Response:**
```json
{
  "prediction": "Normal",
  "xgb_score": 0.12,
  "iso_score": 0.08,
  "final_score": 0.10
}
```

---

## 🔧 Environment Setup (First-time Fresh Install)

If the virtual environments don't exist:

```bash
# Create and install api_env
python3 -m venv api_env
api_env/bin/pip install -r requirements-api.txt

# Create and install ml_env
python3 -m venv ml_env
ml_env/bin/pip install -r requirements-ml.txt
```

Then run the full pipeline:

```bash
make preprocess   # clean & scale data
make train        # train all 3 models
make deploy       # start services
```

---

## 📊 Dataset

- **Source:** [CIC-IDS-2017](https://www.unb.ca/cic/datasets/ids-2017.html) — Canadian Institute for Cybersecurity
- **File:** `data/combinenew.csv` (~830 MB, 80+ features)
- **Training sample:** 50,000 rows (stratified)
- **Labels:** `BENIGN → 0`, all attacks `→ 1`

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| ML | XGBoost, scikit-learn, TensorFlow/Keras |
| Data | Pandas, NumPy |
| Persistence | joblib, HDF5 |
| Python | 3.10 |
