import paho.mqtt.publish as publish
import json
import random
import time
from datetime import datetime
from web3 import Web3


# Set username and password
username = 'utilisateur1'
password = 'User1pwd'

# Connect to Ganache blockchain
provider = Web3.HTTPProvider("http://127.0.0.1:7545")  # Ganache endpoint
web3 = Web3(provider)

if web3.is_connected():
    print("Connected to Ganache blockchain!")
else:
    print("Connection failed. Check the endpoint URL.")


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

    # get contract ABI and address of the deployed smart contract: beekeeper contract
    with open("BeekeeperContract.abi", "r") as f:
        beekeeperContract_abi = f.read()
    beekeeperContract_address = "0x31Ce0cA3c88a9008c63283713588118D32df7177"  # deployed contract address
    # Create contract instance
    beekeeperContract = web3.eth.contract(address=beekeeperContract_address, abi=beekeeperContract_abi)

    # send the beekeeper id as an input to the beekeeeper address function in the smart contract
    beekeeper_address = beekeeperContract.functions.getBeekeeperAddress(beekeeper_id).call()

    # Update beekeeper's values includin beekeeper_id and sender_address in the metadata
    data["beekeeper_id"] = beekeeper_id
    data["sender_address"] = beekeeper_address
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



    #publish.single("metadata", payload=json.dumps(data), hostname="tcp://5.tcp.eu.ngrok.io", port=18698, auth={'username': username, 'password': password})
    publish.single("metadata", payload=json.dumps(data), hostname= '4.tcp.eu.ngrok.io', port=13228)
    print(f"Published message: {json.dumps(data)} to topic metadata")

    time.sleep(5)
