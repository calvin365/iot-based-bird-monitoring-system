import mysql.connector
import csv

# === Connect to MySQL Database ===
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Change if needed
        database="sensor_data"
    )
    cursor = db.cursor()
    print("✅ Connected to database.")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit()

# === Fetch All Sensor Readings ===
query = "SELECT id, latitude, longitude, temperature, humidity, timestamp FROM sensor_readings"
cursor.execute(query)
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

# === Write to CSV ===
csv_file = "sensor_readings_export.csv"
try:
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(columns)  # Write header
        writer.writerows(rows)    # Write data rows
    print(f"✅ Data exported successfully to {csv_file}")
except Exception as e:
    print(f"❌ Failed to export data: {e}")

# === Clean Up ===
cursor.close()
db.close()
