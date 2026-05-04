print("Scientific Model Evaluation Started...")

import pandas as pd
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    auc
)
import matplotlib.pyplot as plt

# ==========================
# Load Data
# ==========================
X = pd.read_csv("data/X_scaled.csv")
y = pd.read_csv("data/y.csv").values.ravel()

# ==========================
# Train-Test Split
# ==========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ==========================
# Load Model
# ==========================
xgb = joblib.load("models/xgb_model.pkl")

# ==========================
# Predict
# ==========================
y_pred = xgb.predict(X_test)
y_proba = xgb.predict_proba(X_test)[:, 1]

# ==========================
# Metrics
# ==========================
print("\n===== TEST PERFORMANCE METRICS =====")

print("Accuracy :", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall   :", recall_score(y_test, y_pred))
print("F1 Score :", f1_score(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ==========================
# ROC Curve
# ==========================
fpr, tpr, thresholds = roc_curve(y_test, y_proba)
roc_auc = auc(fpr, tpr)

plt.figure()
plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.4f}")
plt.plot([0, 1], [0, 1], linestyle='--')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve (Test Data)")
plt.legend()
plt.show()
print("ROC completed")
# ==========================
# Threshold Tuning
# ==========================
print("\n===== THRESHOLD TUNING =====")
print("Starting threshold tuning...")
best_f1 = 0
best_threshold = 0

for t in np.arange(0.1, 0.9, 0.01):
    y_temp = (y_proba >= t).astype(int)
    f1_temp = f1_score(y_test, y_temp)

    if f1_temp > best_f1:
        best_f1 = f1_temp
        best_threshold = t

print("Best Threshold:", round(best_threshold, 2))
print("Best F1 Score :", round(best_f1, 4))


print("\n===== MODEL COMPARISON =====")

iso = joblib.load("models/iso_model.pkl")

iso_scores = -iso.decision_function(X_test)
iso_pred = (iso_scores > np.percentile(iso_scores, 80)).astype(int)

ensemble_score = (0.6 * y_proba) + (0.4 * iso_scores)
ensemble_pred = (ensemble_score >= best_threshold).astype(int)

print("\n--- Isolation Forest ---")
print("F1:", f1_score(y_test, iso_pred))

print("\n--- Ensemble Model ---")
print("F1:", f1_score(y_test, ensemble_pred))


# ==========================
# Cross Validation (5-Fold)
# ==========================
from sklearn.model_selection import cross_val_score

print("\n===== 5-FOLD CROSS VALIDATION =====")

cv_scores = cross_val_score(
    xgb,
    X,
    y,
    cv=5,
    scoring="f1",
    n_jobs=-1
)

print("F1 Scores (each fold):", cv_scores)
print("Mean F1 Score:", round(cv_scores.mean(), 4))
print("Std Deviation:", round(cv_scores.std(), 4))

# ==========================
# Feature Importance
# ==========================
print("\n===== FEATURE IMPORTANCE =====")

importances = xgb.feature_importances_
feature_names = list(X.columns)
print("Feature Columns:", X.columns)
importance_df = pd.DataFrame({
    "Feature": feature_names,
    "Importance": importances
}).sort_values(by="Importance", ascending=False)

print(importance_df.head(10))

# Plot Top 10
plt.figure(figsize=(8,5))
plt.barh(
    importance_df["Feature"].head(10)[::-1],
    importance_df["Importance"].head(10)[::-1]
)
plt.xlabel("Importance Score")
plt.title("Top 10 Important Features")
plt.tight_layout()
plt.savefig("feature_importance.png")
plt.close()