import json
import requests
import paho.mqtt.client as mqtt
from web3 import Web3

# Global variable to store received temperature data
received_temperature_data = None

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

mqtt_client.connect("4.tcp.eu.ngrok.io", 13228, 60)

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
    contract_address = "0xFCf83964198D6d267054200cB7B6D6381052bce5"  # deployed contract address
    # Create contract instance
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    # get contract ABI and address of the deployed smart contract: beekeeper contract
    with open("BeekeeperContract.abi", "r") as f:
        beekeeperContract_abi = f.read()
    beekeeperContract_address = "0x3e100f6CF65df0ba40260584E81E986D9d6Ee484"  # deployed contract address
    # Create contract instance
    beekeeperContract = web3.eth.contract(address=beekeeperContract_address, abi=beekeeperContract_abi)

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
                url = f'https://starknet-mainnet.infura.io/v3/{api_key}'
                payload = {
                    "jsonrpc": "2.0",
                    "method": "starknet_blockHashAndNumber",
                    "params": [],
                    "id": 1
                }
                headers = {'content-type': 'application/json'}
                response = requests.post(url, data=json.dumps(payload), headers=headers).json()
                print(response)
                cid_hash = response["result"]

                # Store the data point and hash in a dictionary
                data_point_with_hash = {'data': entry, 'hash': cid_hash}

                # Append the data point with hash to a list of prepared data
                prepared_data.append(data_point_with_hash)

            # Send prepared data to ganache blockchain
            for entry in prepared_data:
                print(f"- Data point: {entry['data']}")
                print(f"- IPFS Hash: {entry['hash']}")
                # Send IPFS hash to the blockchain
                ipfs_hash = entry['hash']  # Access the IPFS hash from the prepared data
                block_hash = ipfs_hash['block_hash']  # Extract the block_hash (bytes32)
                #block_hash_padded = block_hash.rjust(64, '0')  # Padding with zeros to ensure 32 bytes
                block_hash_bytes32 = web3.to_bytes(hexstr=block_hash)


                # Retrieve beekeeper_id and sender_address from received data
                beekeeper_id = entry["data"]["beekeeper_id"]
                sender_address = entry["data"]["sender_address"]

                # Specify the sender account dynamically based on the beekeeper ID
                sender_account = sender_address

                # Specify the sender account
                transaction = contract.functions.storeIPFSHash(block_hash_bytes32)
                transaction = transaction.build_transaction({
                'from': 'sender_account'  # ganache account address
                })

                # Send the transaction
                transaction_hash = web3.eth.send_transaction(transaction)
                print(f"Transaction hash: {transaction_hash.hex()}")

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
