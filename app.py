# -*- coding: utf-8 -*-
"""Polished Streamlit UI for Network Anomaly Detection

Features:
- Dark theme with gradient background
- Glass‑morphism style cards
- Modern Google Font (Inter)
- Subtle hover and transition effects
- Animated spinner while waiting for prediction
"""

import streamlit as st
import requests

# ---------------------------------------------------------------------------
# Inject custom CSS for premium look & feel
# ---------------------------------------------------------------------------
custom_css = """
/* Google Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

html, body, [data-testid='stAppViewContainer'] {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: #e0e0e0;
    font-family: 'Inter', sans-serif;
}

/* Glass‑morphism card */
.card {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 2rem;
    margin-top: 2rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 30px rgba(0,0,0,0.5);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 40px rgba(0,0,0,0.6);
}

/* Styled button */
.stButton > button {
    background: linear-gradient(45deg, #ff6a00, #ee0979);
    color: white;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
    cursor: pointer;
    transition: background 0.3s ease, transform 0.1s ease;
}
.stButton > button:hover {
    background: linear-gradient(45deg, #ee0979, #ff6a00);
    transform: translateY(-2px);
}

/* Result card */
.result-card {
    background: rgba(0, 0, 0, 0.6);
    border-radius: 10px;
    padding: 1.5rem;
    margin-top: 1rem;
    color: #e0e0e0;
    font-size: 1.1rem;
    line-height: 1.5;
}
"""
st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Page layout
# ---------------------------------------------------------------------------
st.title("🚀 Network Anomaly Detection System")
st.subheader("Enter traffic metrics and let the AI decide if it’s an attack.")

with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        flow_duration = st.number_input("Flow Duration", min_value=0.0, format="%f")
        fwd_packets = st.number_input("Total Fwd Packets", min_value=0.0, format="%f")
    with col2:
        bwd_packets = st.number_input("Total Backward Packets", min_value=0.0, format="%f")
        fwd_length = st.number_input("Total Length of Fwd Packets", min_value=0.0, format="%f")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Predict"):
        # Show a spinner while waiting for the API response
        with st.spinner("🔎 Analyzing traffic..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/predict",
                    json={
                        "Flow_Duration": flow_duration,
                        "Total_Fwd_Packets": fwd_packets,
                        "Total_Backward_Packets": bwd_packets,
                        "Total_Length_of_Fwd_Packets": fwd_length,
                    },
                    timeout=10,
                )
                response.raise_for_status()
                result = response.json()
            except Exception as e:
                st.error(f"❗️ Request failed: {e}")
                st.stop()

        # Display result in a styled card
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.success(f"**Prediction:** {result.get('prediction')}")
        st.write(f"**XGB Score:** {result.get('xgb_score'):.4f}")
        st.write(f"**Isolation Score:** {result.get('iso_score'):.4f}")
        st.write(f"**Final Score:** {result.get('final_score'):.4f}")
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Footer / optional info
# ---------------------------------------------------------------------------
st.caption("© 2026 • Developed by Ramparmeshwar • Powered by FastAPI & Streamlit")
