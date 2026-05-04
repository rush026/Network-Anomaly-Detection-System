import os
import json
import warnings
import smtplib
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from datetime import datetime
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from xgboost import XGBClassifier
from email.message import EmailMessage
from dotenv import load_dotenv

# Local imports
from backend.database import log_anomaly, init_db

# --------------------------------------------------------------
# Configuration & Setup
# --------------------------------------------------------------
load_dotenv()
init_db()

# Suppress version-mismatch warnings
warnings.filterwarnings("ignore", category=UserWarning, module="xgboost")
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

app = FastAPI(title="Network Anomaly Detection API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------
# Model Loading
# --------------------------------------------------------------
print("Loading ensemble models...")

# XGBoost
json_path = os.path.join("models", "xgb_model.json")
if os.path.exists(json_path):
    xgb = XGBClassifier()
    xgb.load_model(json_path)
else:
    xgb = joblib.load(os.path.join("models", "xgb_model.pkl"))

# Compatibility fixes for CPU-only environment
setattr(xgb, "use_label_encoder", False)
setattr(xgb, "gpu_id", -1)
setattr(xgb, "predictor", "cpu_predictor")

# Isolation Forest, Autoencoder, and Scaler
iso = joblib.load(os.path.join("models", "iso_model.pkl"))
ae = tf.keras.models.load_model(os.path.join("models", "autoencoder.h5"))
scaler = joblib.load(os.path.join("models", "scaler.pkl"))

print("Ensemble models loaded successfully ✅")

THRESHOLD: float = float(os.getenv("ANOMALY_THRESHOLD", "0.5"))
FEATURES_LIST = [
    'Flow Duration',
    'Total Fwd Packets',
    'Total Backward Packets',
    'Total Length of Fwd Packets'
]

# --------------------------------------------------------------
# Schemas & Helpers
# --------------------------------------------------------------
class TrafficData(BaseModel):
    Flow_Duration: float
    Total_Fwd_Packets: float
    Total_Backward_Packets: float
    Total_Length_of_Fwd_Packets: float

class TrafficDataBatch(BaseModel):
    data: List[TrafficData]

def send_alert_email(probability: float) -> None:
    sender = os.getenv("ALERT_EMAIL_SENDER")
    receiver = os.getenv("ALERT_EMAIL_RECEIVER")
    password = os.getenv("ALERT_EMAIL_PASSWORD")

    if not all([sender, receiver, password]):
        print("Warning: Email credentials missing. Skipping alert email.")
        return

    msg = EmailMessage()
    msg["Subject"] = "⚠ Network Anomaly Detected!"
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content(f"Alert!\n\nSuspicious traffic detected.\nAttack Probability: {probability:.4f}\n\nPlease investigate immediately.")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            print(f"Alert email sent to {receiver}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# --------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------
@app.get("/")
def home():
    return {"message": "Network Anomaly Detection API Running", "ensemble": ["XGBoost", "Isolation Forest", "Autoencoder"]}

@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": True}

@app.post("/predict")
def predict(data: TrafficData):
    input_vals = [data.Flow_Duration, data.Total_Fwd_Packets, data.Total_Backward_Packets, data.Total_Length_of_Fwd_Packets]
    arr = np.array([input_vals])
    arr_scaled = scaler.transform(arr)
    
    # XGBoost (needs DataFrame with names)
    df_scaled = pd.DataFrame(arr_scaled, columns=FEATURES_LIST)
    xgb_score = float(xgb.predict_proba(df_scaled)[0][1])
    
    # Isolation Forest
    iso_score = float(max(0.0, -iso.decision_function(arr_scaled)[0]))
    
    # Autoencoder
    recon = ae.predict(arr_scaled, verbose=0)
    ae_score = float(np.mean((arr_scaled - recon) ** 2))
    ae_score = min(1.0, ae_score)  # Cap at 1.0 for ensemble stability
    
    # Ensemble (Weighted)
    final_score = (0.4 * xgb_score) + (0.3 * iso_score) + (0.3 * ae_score)
    label = "Attack" if final_score > THRESHOLD else "Normal"
    
    if label == "Attack":
        # Text log
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("attack_log.txt", "a") as f:
            f.write(f"[{ts}] Anomaly Detected! Score: {final_score:.4f}, Details: {input_vals}\n")
        
        # Postgres log
        try:
            log_anomaly(label, xgb_score, iso_score, ae_score, final_score, json.dumps(input_vals))
        except Exception as e:
            print(f"DB Log Error: {e}")

        # Alert
        send_alert_email(final_score)

    return {
        "prediction": label,
        "xgb_score": xgb_score,
        "iso_score": iso_score,
        "ae_score": ae_score,
        "final_score": final_score,
    }

@app.post("/predict_batch")
def predict_batch(batch: TrafficDataBatch):
    results = []
    for record in batch.data:
        res = predict(record) # Reuse single predict logic for consistency
        results.append(res)
    return {"results": results}