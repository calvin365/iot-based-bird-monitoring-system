import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import mysql.connector
import numpy as np
import joblib
import smtplib
import ssl
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tensorflow.keras.models import load_model
from tensorflow.keras.losses import MeanSquaredError
import tensorflow as tf

# === Custom Metric for Model Loading ===
def gps_accuracy(y_true, y_pred, threshold=0.05):
    abs_error = tf.abs(y_true - y_pred)
    accurate = tf.reduce_all(tf.less(abs_error, threshold), axis=1)
    accuracy = tf.reduce_mean(tf.cast(accurate, tf.float32))
    return accuracy * 100

# === Load Trained Model and Scaler ===
try:
    model = load_model('bird_migration_model.h5', custom_objects={
        'mse': MeanSquaredError(),
        'gps_accuracy': gps_accuracy
    })
    scaler = joblib.load('scaler.save')
except Exception as e:
    print(f"❌ Error loading model or scaler: {e}")
    exit()

# === Connect to MySQL Database ===
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Update if needed
        database="sensor_data"
    )
    cursor = db.cursor()
except Exception as e:
    print(f"❌ Failed to connect to database: {e}")
    exit()

# === Fetch Latest Sensor Readings ===
cursor.execute("SELECT latitude, longitude, temperature, humidity FROM sensor_readings ORDER BY id DESC LIMIT 10")
rows = cursor.fetchall()

if len(rows) < 10:
    print("❌ Not enough data in the database (need 10 rows).")
    cursor.close()
    db.close()
    exit()

# === Prepare Data ===
X = np.array(rows).astype(np.float32).reshape(1, 10, 4)
X_scaled = scaler.transform(X[0]).reshape(1, 10, 4)

# === Predict & Check Anomaly ===
predicted = model.predict(X_scaled)
true = X_scaled[:, -1, :2]  # Last timestep actual [lat, lon]
pred = predicted[:, :2]

error = np.mean(np.abs(true - pred))  # Mean Absolute Error
print(f"📊 Prediction error: {error:.4f}")

# === Anomaly Threshold ===
THRESHOLD = 0.15
anomaly_detected = error > THRESHOLD

# Get just the last 3 readings for the alert
last_three_rows = rows[:3]

# === Save output to JSON file ===
output = {
    "error": round(float(error), 4),
    "anomaly": bool(anomaly_detected),  # Convert np.bool_ to Python bool
    "sensor_data": [list(row) for row in rows]  # Convert tuples to lists for JSON
}

with open("output.json", "w") as f:
    json.dump(output, f)

# === Email Credentials ===
sender = "calvinochieng365@gmail.com"
receiver = "calvin365000@gmail.com"
password = "sbqs tdwt yoht zrxl"  # Gmail App Password

# === Generate Targeted Recommendations ===
def get_targeted_recommendations(rows):
    lat, lon, temp, humidity = rows[0]  # Get most recent reading
    
    recommendations = []
    
    # Temperature-based recommendations
    if temp > 35:
        recommendations.append("CRITICAL: Extreme heat detected. Birds may be at risk of dehydration and heat stress.")
        recommendations.append("Provide additional water sources and shaded areas immediately.")
    elif temp > 30:
        recommendations.append("WARNING: High temperature detected. Monitor birds for signs of heat stress.")
    elif temp < 5:
        recommendations.append("CRITICAL: Low temperature detected. Birds may be at risk of hypothermia.")
        recommendations.append("Ensure adequate shelter and protection from wind.")
        
    # Humidity-based recommendations
    if humidity > 90:
        recommendations.append("High humidity detected. Check for mold or respiratory issues in the habitat.")
    elif humidity < 20:
        recommendations.append("Low humidity detected. Ensure adequate water sources for birds.")
    
    # Movement pattern recommendations
    if error > 0.3:
        recommendations.append("URGENT: Severe deviation from expected pattern detected.")
        recommendations.append("Investigate potential environmental disruptions or predator activity.")
    elif error > 0.15:
        recommendations.append("Significant deviation from expected migration pattern detected.")
        recommendations.append("Consider increased monitoring frequency.")
    
    # Default recommendations if none were added
    if not recommendations:
        recommendations = [
            "Verify sensor calibration and battery levels.",
            "Conduct routine habitat inspection.",
            "Document current conditions for baseline comparison."
        ]
        
    return recommendations

# === Send Email Alert If Needed ===
if anomaly_detected:
    print("⚠️ Anomaly Detected! Sending alert email...")
    
    # Get targeted recommendations based on the data
    recommendations = get_targeted_recommendations(rows)

    # Create multipart message
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = "🔥 ALERT: Bird Migration Anomaly Detected"

    # Body of the email with only the last 3 readings
    body = f"""
    🚨 WARNING: Anomaly detected in bird migration patterns. Immediate attention required.

    📉 Deviation Score: {error:.4f} (Threshold: {THRESHOLD})

    📍 Latest Sensor Readings (most recent first):
    """

    # Attach the body to the email
    msg.attach(MIMEText(body, "plain"))

    # Table header
    msg.attach(MIMEText("\nTimestamp | Latitude | Longitude | Temperature (°C) | Humidity (%)\n" + 
                        "-" * 65 + "\n", "plain"))

    # Add only the last 3 sensor data points as part of the email
    for i, row in enumerate(last_three_rows):
        data_line = f"Reading {i+1} | {row[0]:.6f} | {row[1]:.6f} | {row[2]:.1f}°C | {row[3]:.1f}%\n"
        msg.attach(MIMEText(data_line, "plain"))

    # Actionable information and recommended steps
    msg.attach(MIMEText(f"""
    -----------------------------
    📋 RECOMMENDED ACTIONS:
    """, "plain"))

    # List the specific recommended actions for the anomaly
    for action in recommendations:
        msg.attach(MIMEText(f"• {action}\n", "plain"))

    msg.attach(MIMEText(f"""
    -----------------------------
    📱 Contact: Field Response Team at +254 740 4297 97
    🔗 View detailed analytics: file:///C:/xampp/htdocs/PROJECT/index.html
    
    This is an automated alert from the Bird Migration Monitoring System.
    Please acknowledge receipt of this alert by replying to this email.
    """, "plain"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print("✅ Email alert sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
else:
    print("✅ No anomaly detected. All readings within normal parameters.")

# === Clean Up ===
cursor.close()
db.close()