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


# get contract ABI and address of the deployed smart contract: beekeeper contract
with open("BeekeeperContract.abi", "r") as f:
    beekeeperContract_abi = f.read()
beekeeperContract_address = "0x3e100f6CF65df0ba40260584E81E986D9d6Ee484"  # deployed contract address
# Create contract instance
beekeeperContract = web3.eth.contract(address=beekeeperContract_address, abi=beekeeperContract_abi)


while True:
    # Generate random beekeeper_id
    beekeeper_id = random.randint(1, 4)

    # Retrieve the beekeeper's Ethereum address from the smart contract
    beekeeper_address = beekeeperContract.functions.getBeekeeperAddress(beekeeper_id).call()

    # Generate initial data for the beekeeper
    hive_id = beekeeper_id
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

    # Construct the data payload
    data = {
        "beekeeper_id": beekeeper_id,
        "beekeeper_address": beekeeper_address,
        "hive_id": hive_id,
        "temperature": temperature, 
        "humidity": humidity,
        "co2": co2,
        "weight": weight,
        "gps_location": gps_location,
        "hasPests": has_pests,
        "hasDiseases": has_diseases,
        "latitude": latitude,
        "longitude": longitude,
        "has_pests": has_pests,
        "has_diseases": has_diseases,
        "timestamp": timestamp
    }

    # Publish the data
    publish.single("metadata", payload=json.dumps(data), hostname= '6.tcp.eu.ngrok.io', port=10180)
    print(f"Published message: {json.dumps(data)} to topic metadata")

    # Wait for the next iteration
    time.sleep(5)
