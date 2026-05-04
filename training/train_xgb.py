print("Script started...")
import pandas as pd
import joblib
from xgboost import XGBClassifier

# Load processed data
X = pd.read_csv("data/X_scaled.csv")
y = pd.read_csv("data/y.csv")

# Create model
model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')

# Train model
model.fit(X, y.values.ravel())

# Save model
joblib.dump(model, "models/xgb_model.pkl")

print("XGBoost model trained and saved ✅")
