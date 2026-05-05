import streamlit as st
import requests
import os
import pandas as pd
import numpy as np
import sys
# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.database import get_recent_logs

st.title("Network Anomaly Detection System")

# API URL Configuration
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Input fields
flow_duration = st.number_input("Flow Duration", value=1000)
fwd_packets = st.number_input("Total Fwd Packets", value=10)
bwd_packets = st.number_input("Total Backward Packets", value=5)
fwd_length = st.number_input("Total Length of Fwd Packets", value=500)

# Button click
if st.button("Predict"):

    try:
        response = requests.post(
            f"{API_URL}/predict",
            json={
                "Flow_Duration": flow_duration,
                "Total_Fwd_Packets": fwd_packets,
                "Total_Backward_Packets": bwd_packets,
                "Total_Length_of_Fwd_Packets": fwd_length
            }
        )

        st.success("Prediction Result:")
        res = response.json()
        st.json(res)
        
        # Display Bar Chart for individual model scores
        st.subheader("Ensemble Breakdown")
        scores_df = pd.DataFrame({
            "Model": ["XGBoost", "Isolation Forest", "Autoencoder", "Final Score"],
            "Score": [res["xgb_score"], res["iso_score"], res["ae_score"], res["final_score"]]
        })
        st.bar_chart(scores_df.set_index("Model"))

    except Exception as e:
        st.error(f"Error connecting to API: {e}")

st.divider()
st.subheader("Real-Time Anomaly Trend (PostgreSQL)")

try:
    recent_logs = get_recent_logs(limit=50)
    if recent_logs:
        df_db = pd.DataFrame(recent_logs)
        # Ensure timestamp is datetime and sort
        df_db["timestamp"] = pd.to_datetime(df_db["timestamp"])
        df_db = df_db.sort_values("timestamp")
        
        st.line_chart(df_db.set_index("timestamp")["final_score"])
        
        st.subheader("Recent Anomaly Logs (PostgreSQL)")
        st.dataframe(df_db.sort_values("timestamp", ascending=False)[["timestamp", "prediction", "final_score", "details"]])
    else:
        st.info("No logs found in PostgreSQL. Anomaly detections will appear here.")
except Exception as e:
    st.error(f"Error fetching from PostgreSQL: {e}")
    st.info("Ensure PostgreSQL is running and credentials are correct in .env")

# Fallback/Legacy Log viewer
with st.expander("Show Legacy Text Logs"):
    if os.path.exists("attack_log.txt"):
        with open("attack_log.txt", "r") as f:
            logs = f.readlines()
        for log in reversed(logs[-10:]):
            st.text(log.strip())
    else:
        st.info("No legacy logs found.")
