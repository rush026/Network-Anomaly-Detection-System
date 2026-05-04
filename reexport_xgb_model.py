# reexport_xgb_model.py
"""Utility script to re‑export the XGBoost model in the native XGBoost format.

Why?
- The pickle file (`models/xgb_model.pkl`) was created with an older XGBoost version.
- Loading it with the current XGBoost version triggers a warning about
  serialization incompatibility.
- Saving the model with `model.save_model('models/xgb_model.json')` produces a
  version‑compatible file that can be loaded with `xgboost.Booster` or via
  `XGBClassifier` without warnings.

Usage (run inside the project's virtual environment):
```bash
source api_env/bin/activate
python reexport_xgb_model.py
```
The script will:
1. Load the existing pickle model (`models/xgb_model.pkl`).
2. Save it to `models/xgb_model.json` (native XGBoost format).
3. Optionally replace the pickle file with the new one if you uncomment the
   cleanup lines.
"""

import joblib
import os
import warnings

# Suppress the warning that appears when loading the old pickle
warnings.filterwarnings("ignore", category=UserWarning, module="xgboost")

MODEL_PKL = os.path.join("models", "xgb_model.pkl")
MODEL_JSON = os.path.join("models", "xgb_model.json")

if not os.path.exists(MODEL_PKL):
    raise FileNotFoundError(f"Pickle model not found at {MODEL_PKL}")

# Load the old pickle model
xgb_model = joblib.load(MODEL_PKL)

# Save in native XGBoost format
xgb_model.save_model(MODEL_JSON)

print(f"✅ Model re‑exported to {MODEL_JSON}")

# Uncomment the following lines if you want to replace the pickle with the JSON version
# os.remove(MODEL_PKL)
# print(f"Removed old pickle model {MODEL_PKL}")
