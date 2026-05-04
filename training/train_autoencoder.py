print("Autoencoder Training Started...")

import pandas as pd
import tensorflow as tf
import numpy as np

# Load processed data
X = pd.read_csv("data/X_scaled.csv")
X = X.values

print("Data Loaded")
print("Shape:", X.shape)

input_dim = X.shape[1]

# Build Autoencoder
model = tf.keras.Sequential([
    tf.keras.layers.Dense(16, activation='relu', input_shape=(input_dim,)),
    tf.keras.layers.Dense(8, activation='relu'),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(input_dim)
])

model.compile(optimizer='adam', loss='mse')

# Train
model.fit(
    X, X,
    epochs=10,
    batch_size=32,
    verbose=1
)

# Save model
model.save("models/autoencoder.h5")

print("Autoencoder trained and saved ✅")

