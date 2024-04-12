import json
import requests
import paho.mqtt.client as mqtt
from web3 import Web3
import base58

# Global variable to store received temperature data
received_beekeeper_metadata = None

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("metadata")

def on_message(client, userdata, msg):
    global received_beekeeper_metadata
    received_beekeeper_metadata = json.loads(msg.payload.decode())
    print(f"received the metadata of the beekeeper: {received_beekeeper_metadata}")

# MQTT setup
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect("127.0.0.1", 1883, 60)

if __name__ == "__main__":
    # Subscribe to MQTT topic
    mqtt_client.loop_start()

    # Connect to Ganache blockchain
    provider = Web3.HTTPProvider("http://127.0.0.1:7545")  # Ganache endpoint
    web3 = Web3(provider)

    if web3.is_connected():
        print("Connected to Ganache blockchain!")
    else:
        print("Connection failed. Check the endpoint URL.")

    # get contract ABI and address of the deployed smart contract: storeHash contract
    with open("StoreHashContract.abi", "r") as f:
        contract_abi = f.read()
    contract_address = "0x357CbccF44B966007bd482fF08f7Df82b7F5f2eD"  # deployed contract address
    # Create contract instance
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    # get contract ABI and address of the deployed smart contract: beekeeper contract
    with open("BeekeeperContract.abi", "r") as f:
        beekeeperContract_abi = f.read()
    beekeeperContract_address = "0xD5E8B3078A5609ff63eDfB5A360cCE169f2b27c3"  # deployed contract address
    # Create contract instance
    beekeeperContract = web3.eth.contract(address=beekeeperContract_address, abi=beekeeperContract_abi)

    try:
        while True:
            # Wait for temperature data from MQTT broker
            while received_beekeeper_metadata is None:
                pass

            # Use received temperature data
            data = [received_beekeeper_metadata]

            # Prepare data for IPFS
            prepared_data = []
            for entry in data:
                # Convert each data point to JSON format
                entry_json = json.dumps(entry)

                # Send the data to Pinata
                url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
                headers = {
                    "Content-Type": "application/json",
                    "pinata_api_key": "d4ff07b0e166ec5b7db8",
                    "pinata_secret_api_key": "1da36dca5acaa1640cf937790bf16129e9dc9d97c6c1d32df5c16d402b0ed0da"
                }
                response = requests.post(url, json={"pinataMetadata": {"name": "Metadata"}, "pinataContent": entry_json}, headers=headers)
                
                if response.status_code == 200:
                    # Retrieved CID hash from Pinata's response
                    try:
                        cid_hash = response.json()["IpfsHash"]
                        print(cid_hash)
                        print(f"Received CID hash from Pinata: {cid_hash}")

                        # Store the data point and hash in a dictionary
                        data_point_with_hash = {'data': entry, 'hash': cid_hash}

                        # Append the data point with hash to a list of prepared data
                        prepared_data.append(data_point_with_hash)
                    except KeyError:
                        print("Failed to retrieve CID hash from Pinata response. Response format may be unexpected.")
                else:
                    print(f"Failed to pin data to Pinata. Status code: {response.status_code}")
                    continue  # Skip to the next iteration of the loop

            # Send prepared data to ganache blockchain
            for entry in prepared_data:
                print(f"- Data point: {entry['data']}")
                print(f"- IPFS Hash: {entry['hash']}")
                # Send IPFS hash to the blockchain
                ipfs_hash = entry['hash']  # Access the IPFS hash from the prepared data
                ipfs_bytes = base58.b58decode(ipfs_hash)# Decode the IPFS hash from Base58
                block_hash_bytes32 = ipfs_bytes[-32:]# Extract the last 32 bytes to get the bytes32 representation

                # Retrieve beekeeper_id and sender_address from received data
                beekeeper_id = entry["data"]["beekeeper_id"]
                sender_address = entry["data"]["beekeeper_address"]

                # Specify the sender account dynamically based on the beekeeper ID
                sender_account = sender_address

                # Specify the sender account
                transaction = contract.functions.storeIPFSHash(block_hash_bytes32)
                transaction = transaction.build_transaction({
                'from': sender_account,  # ganache account address
                'gas': 200000
                })

                # Send the transaction
                transaction_hash = web3.eth.send_transaction(transaction)
                print(f"Transaction hash: {transaction_hash.hex()}")

                # Call the function from the second smart contract
                beekeeperContract.functions.getBeekeeperAddress(beekeeper_id).transact({'from': sender_account})

            # Clear the prepared data list after sending to IPFS
            del prepared_data

            # Check if 'prepared_data' still exists
            try:
                print(prepared_data)  # This will raise a NameError if 'prepared_data' is deleted
            except NameError as e:
                print(f"prepared_data has been deleted from memory: {e}")

            # Reset received_temperature_data for the next iteration
            received_temperature_data = None


    except KeyboardInterrupt:
        print("Program terminated by user")
        mqtt_client.loop_stop()
