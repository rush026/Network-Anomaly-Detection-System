import joblib
import numpy as np
import tensorflow as tf

print("Loading models...")

# Load models
xgb = joblib.load("models/xgb_model.pkl")
iso = joblib.load("models/iso_model.pkl")
scaler = joblib.load("models/scaler.pkl")
ae = tf.keras.models.load_model("models/autoencoder.h5")

print("Models loaded successfully ✅")

def predict(input_data):
    """
    input_data: list of 4 feature values
    """

    # Convert to numpy
    data = np.array([input_data])

    # Scale
    data_scaled = scaler.transform(data)

    # XGBoost score
    xgb_score = xgb.predict_proba(data_scaled)[0][1]

    # Isolation Forest score
    iso_score = iso.decision_function(data_scaled)[0]

    # Autoencoder reconstruction error
    recon = ae.predict(data_scaled)
    ae_score = np.mean((data_scaled - recon) ** 2)

    # Weighted Ensemble
    final_score = (0.4 * xgb_score) + (0.3 * iso_score) + (0.3 * ae_score)

    label = "Attack" if final_score > 0.5 else "Normal"

    return {
        "xgb_score": float(xgb_score),
        "iso_score": float(iso_score),
        "ae_score": float(ae_score),
        "final_score": float(final_score),
        "prediction": label
    }
    if final_score > THRESHOLD:
     prediction = "Attack"
     send_alert_email("kuchh galat chij aa gyi re mujhhe sahi kar de re ")

    else:
      prediction = "Normal"

# Test run
if __name__ == "__main__":
    sample = [1000, 10, 5, 500]  # example input
    result = predict(sample)
    print(result)

