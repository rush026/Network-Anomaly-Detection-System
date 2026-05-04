import pandas as pd
from sklearn.preprocessing import StandardScaler

import joblib

print("Preprocessing started...")

# Load dataset
df = pd.read_csv("data/combinenew.csv", low_memory=False)

# Remove leading/trailing spaces from column names
df.columns = df.columns.str.strip()

print("Columns cleaned")
print("Shape:", df.shape)

# OPTIONAL: dataset छोटा कर दो (fast training के लिए)
df = df.sample(50000, random_state=42)

# Drop missing values
df = df.dropna()

# Encode label
df['Label'] = df['Label'].apply(lambda x: 0 if x == 'BENIGN' else 1)

# Select correct feature names (spaces removed now)
features = [
    'Flow Duration',
    'Total Fwd Packets',
    'Total Backward Packets',
    'Total Length of Fwd Packets'
]

X = df[features]
y = df['Label']

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

# Save scaler
joblib.dump(scaler, "models/scaler.pkl")

# Save processed files
pd.DataFrame(X_scaled).to_csv("data/X_scaled.csv", index=False)
pd.DataFrame(y).to_csv("data/y.csv", index=False)

print("Preprocessing completed successfully ✅")

