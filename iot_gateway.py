import json
import requests
import paho.mqtt.client as mqtt

# Global variable to store received temperature data
received_temperature_data = None

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("temperature")

def on_message(client, userdata, msg):
    global received_temperature_data
    received_temperature_data = json.loads(msg.payload.decode())
    print(f"Received temperature data: {received_temperature_data}")

# MQTT setup
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect("127.0.0.1", 1883, 60)

if __name__ == "__main__":
    # Subscribe to MQTT topic
    mqtt_client.loop_start()

    try:
        while True:
            # Wait for temperature data from MQTT broker
            while received_temperature_data is None:
                pass

            # Use received temperature data
            data = [received_temperature_data]

            # Prepare data for IPFS
            prepared_data = []
            for entry in data:
                # Convert each data point to JSON format
                entry_json = json.dumps(entry)

                # Send the data to IPFS and get the CID hash
                api_key = "683524b9a0da412bb1fa3a08433cfe6e"
                url = f"https://starknet-mainnet.infura.io/v3/{api_key}"
                headers = {"Content-Type": "application/json"}
                data = {
                    "jsonrpc": "2.0",
                    "method": "starknet_blockHashAndNumber",
                    "params": [],
                    "id": 1
                }
                response = requests.post(url, headers=headers, json=data)
                cid_hash = response.json()["result"]

                # Store the data point and hash in a dictionary
                data_point_with_hash = {'data': entry, 'hash': cid_hash}

                # Append the data point with hash to a list of prepared data
                prepared_data.append(data_point_with_hash)

            # Send prepared data to Remix blockchain
            for entry in prepared_data:
                print(f"- Data point: {entry['data']}")
                print(f"- IPFS Hash: {entry['hash']}")

            # Reset received_temperature_data for the next iteration
            received_temperature_data = None

    except KeyboardInterrupt:
        print("Program terminated by user")
        mqtt_client.loop_stop()
