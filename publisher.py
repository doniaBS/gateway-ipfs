import paho.mqtt.publish as publish
import json
import random
import time

while True:
    temperature = random.uniform(20.0, 30.0)
    data = {"temperature": temperature, "timestamp": int(time.time())}

    publish.single("temperature", payload=json.dumps(data), hostname="127.0.0.1", port=1883)
    print(f"Published message: {json.dumps(data)} to topic temperature")

    time.sleep(5)
