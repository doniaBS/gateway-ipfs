import paho.mqtt.publish as publish
import json
import random
import time
from datetime import datetime

# Counter for beekeeper IDs
beekeeper_id_counter = 1

# Function to generate random data
def generate_data():

    global beekeeper_id_counter

    temperature = round(random.uniform(20.0, 30.0), 2)
    humidity = round(random.uniform(40.0, 50.0), 2)
    co2 = round(random.uniform(60.0, 70.0), 2)
    weight = round(random.uniform(80.0, 90.0), 2)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Increment beekeeper ID counter for next beekeeper
    beekeeper_id = beekeeper_id_counter
    beekeeper_id_counter += 1
    return {
        "beekeeper_id": beekeeper_id, 
        "temperature": temperature, 
        "humidity": humidity,
        "co2": co2,
        "weight": weight,
        "timestamp": timestamp,
        }

while True:
    data = generate_data()

    publish.single("metadata", payload=json.dumps(data), hostname="127.0.0.1", port=1883)
    print(f"Published message: {json.dumps(data)} to topic metadata")

    time.sleep(5)
