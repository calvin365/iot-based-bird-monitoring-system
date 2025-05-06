import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
import joblib

# === Load Data ===
df = pd.read_csv("sensor_readings_export.csv")

# === Prepare Sequences ===
sequence_length = 10
features = ["latitude", "longitude", "temperature", "humidity"]

data = df[features].values.astype(np.float32)

scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)

X, y = [], []

for i in range(len(data_scaled) - sequence_length):
    X.append(data_scaled[i:i+sequence_length])
    y.append(data_scaled[i+sequence_length][:2])  # Predict lat/lon

X = np.array(X)
y = np.array(y)

# === Train/Test Split ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === Build Model ===
model = Sequential([
    LSTM(64, input_shape=(X.shape[1], X.shape[2])),
    Dense(2)  # Only predicting latitude & longitude
])

model.compile(optimizer='adam', loss='mse')

# === Train Model ===
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

model.fit(X_train, y_train, validation_data=(X_test, y_test),
          epochs=50, batch_size=16, callbacks=[early_stop])

# === Evaluate Model ===
loss = model.evaluate(X_test, y_test)
print(f"✅ Final Validation Loss: {loss:.4f}")

# === Save Model and Scaler ===
model.save("bird_migration_model.h5")
joblib.dump(scaler, "scaler.save")
print("✅ Model & scaler saved.")
