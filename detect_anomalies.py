#!/usr/bin/env python3
"""Detect anomalies in a CSV dataset using the trained XGBoost and Isolation Forest models.

Usage:
    python detect_anomalies.py --input data.csv --output results.csv

The input CSV should contain the same feature columns used for training:
    Flow_Duration, Total_Fwd_Packets, Total_Backward_Packets, Total_Length_of_Fwd_Packets

The script will output a CSV with the original columns plus:
    prediction, xgb_score, iso_score, final_score
"""

import argparse
import pandas as pd
import joblib
import numpy as np

def load_models(model_dir: str = "models"):
    xgb = joblib.load(f"{model_dir}/xgb_model.pkl")
    iso = joblib.load(f"{model_dir}/iso_model.pkl")
    scaler = joblib.load(f"{model_dir}/scaler.pkl")
    return xgb, iso, scaler

def predict_batch(df: pd.DataFrame, xgb, iso, scaler):
    # Ensure correct column order
    feature_cols = ["Flow_Duration", "Total_Fwd_Packets", "Total_Backward_Packets", "Total_Length_of_Fwd_Packets"]
    arr = df[feature_cols].values
    arr_scaled = scaler.transform(arr)
    xgb_scores = xgb.predict_proba(arr_scaled)[:, 1]
    iso_scores = np.maximum(0.0, -iso.decision_function(arr_scaled))
    final_scores = 0.5 * xgb_scores + 0.5 * iso_scores
    predictions = np.where(final_scores > 0.5, "Attack", "Normal")
    df["prediction"] = predictions
    df["xgb_score"] = xgb_scores.astype(float)
    df["iso_score"] = iso_scores.astype(float)
    df["final_score"] = final_scores.astype(float)
    return df

def main():
    parser = argparse.ArgumentParser(description="Detect anomalies in a CSV dataset.")
    parser.add_argument("--input", required=True, help="Path to input CSV file.")
    parser.add_argument("--output", required=True, help="Path to output CSV file with predictions.")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    xgb, iso, scaler = load_models()
    result_df = predict_batch(df, xgb, iso, scaler)
    result_df.to_csv(args.output, index=False)
    print(f"✅ Anomaly detection completed. Results saved to {args.output}")

if __name__ == "__main__":
    main()
