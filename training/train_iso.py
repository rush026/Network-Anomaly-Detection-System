print("Isolation Forest Training Started...")

import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest

# Load processed data
X = pd.read_csv("data/X_scaled.csv")

print("Data Loaded")
print("Shape:", X.shape)

# Train Isolation Forest
iso = IsolationForest(
    n_estimators=100,
    contamination=0.1,
    random_state=42
)

iso.fit(X)

# Save model
joblib.dump(iso, "models/iso_model.pkl")

print("Isolation Forest trained and saved ✅")

