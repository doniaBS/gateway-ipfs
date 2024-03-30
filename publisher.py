import paho.mqtt.publish as publish
import json
import random
import time
from datetime import datetime

# Generate initial data for 4 beekeepers
beekeepers_data = {}
for i in range(1, 5):
    hive_id = i
    temperature = round(random.uniform(20.0, 30.0), 2)
    humidity = round(random.uniform(40.0, 50.0), 2)
    co2 = round(random.uniform(60.0, 70.0), 2)
    weight = round(random.uniform(80.0, 90.0), 2)
    latitude = round(random.uniform(10.0, 50.0), 6) 
    longitude = round(random.uniform(10.0, 50.0), 6)
    gps_location = f"{latitude},{longitude}"  # Combine latitude and longitude
    has_pests = random.choice([True, False]) # Generate random boolean values for hasPests
    has_diseases = random.choice([True, False]) # Generate random boolean values for hasDiseases
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    beekeepers_data[i] = {
        "hive_id": hive_id,
        "temperature": temperature, 
        "humidity": humidity,
        "co2": co2,
        "weight": weight,
        "gps_location": gps_location,
        "hasPests": has_pests,
        "hasDiseases": has_diseases,  
        "timestamp": timestamp
    }

while True:
    # Select a beekeeper randomly
    beekeeper_id = random.randint(1, 4)
    data = beekeepers_data[beekeeper_id]

    # Update beekeeper's values
    data["hive_id"] = i
    data["temperature"] = round(random.uniform(20.0, 30.0), 2)
    data["humidity"] = round(random.uniform(40.0, 50.0), 2)
    data["co2"] = round(random.uniform(60.0, 70.0), 2)
    data["weight"] = round(random.uniform(80.0, 90.0), 2)
    data["latitude"] = round(random.uniform(10.0, 50.0), 6) 
    data["longitude"] = round(random.uniform(10.0, 50.0), 6)
    data["gps_location"] = f"{latitude},{longitude}"
    data["has_pests"] = random.choice([True, False])
    data["has_diseases"] = random.choice([True, False])
    data["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    publish.single("metadata", payload=json.dumps(data), hostname="127.0.0.1", port=1883)
    print(f"Published message: {json.dumps(data)} to topic metadata")

    time.sleep(5)
