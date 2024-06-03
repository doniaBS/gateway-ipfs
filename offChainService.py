import json
import requests
from web3 import Web3
import base58
from websocket_server import WebsocketServer
import threading

# Global variable for the WebSocket server
ws_server = None

def handle_event(event):
    beekeeper_address = event['args']['beekeeperAddress']
    ipfs_hash_bytes32 = event['args']['retrievedHash']
    print(f"Received IPFS hash (bytes32): {ipfs_hash_bytes32.hex()} for beekeeper address: {beekeeper_address}")

    # Convert bytes32 hash to base58
    ipfs_hash_bytes = Web3.to_bytes(ipfs_hash_bytes32)
    
    # Prepend the first 2 bytes of the IPFS hash (Qm)
    ipfs_hash_bytes_full = b'\x12\x20' + ipfs_hash_bytes

    ipfs_hash_base58 = base58.b58encode(ipfs_hash_bytes_full).decode('utf-8')
    print(ipfs_hash_base58)

    # Construct the request URL
    pinata_gateway = 'https://gateway.pinata.cloud/ipfs/'
    request_url = f"{pinata_gateway}{ipfs_hash_base58}"

    # Make the HTTP request to IPFS
    response = requests.get(request_url)
    if response.status_code == 200:
        metadata = response.json()
        print(f"Retrieved metadata: {metadata}")
        # Send metadata to webpage
        send_to_web_page(metadata)  
        # Send the metadata to the BeekeeperContract
        send_to_beekeeper_contract(metadata)
        return True
    else:
        error_message = "Failed to retrieve metadata from IPFS. Data has been changed"
        print(error_message)
        return False

def send_to_beekeeper_contract(metadata):
    provider = Web3.HTTPProvider("http://127.0.0.1:7545")
    web3 = Web3(provider)

    if not web3.is_connected():
        print("Failed to connect to Ganache blockchain")
        return

    # Load contract BeekeeperContract ABI and address
    with open("BeekeeperContract.abi", "r") as f:
        beekeeperContract_abi = f.read()
    beekeeperContract_address = "0x63039B71C8E19bE6270370783ee407850409DcC8"  # Deployed contract address

    # Create contract instance
    contractBeekeeper = web3.eth.contract(address=beekeeperContract_address, abi=beekeeperContract_abi)
    # send the metadata to the corresponding data in the smart contract
    metadata_processing = json.loads(metadata) #convert it to pyton dic to access to the metadata attributes
    hive_id = int(metadata_processing["hive_id"])
    print(hive_id)
    beekeeperId = int(metadata_processing["beekeeper_id"])
    beekeeperAddress = metadata_processing["beekeeper_address"]
    temperature = int(metadata_processing["temperature"])
    print(temperature)
    humidity = int(metadata_processing["humidity"])
    co2 = int(metadata_processing["co2"])
    weight = int(metadata_processing["weight"])
    hasPests = bool(metadata_processing["hasPests"])
    print(hasPests)
    hasDiseases = bool(metadata_processing["hasDiseases"])

    # register beekeepers
    register_beekeeper(web3, contractBeekeeper, beekeeperId, beekeeperAddress)

    #register the hives to the beekeeperId
    register_hive(web3, contractBeekeeper, hive_id, beekeeperId, beekeeperAddress)
    
    # Process the metadata and update the hive state
    process_metadata(web3, contractBeekeeper, hive_id, beekeeperAddress, temperature, humidity, co2, weight, hasPests, hasDiseases)

def register_beekeeper(web3, contract, beekeeperId, beekeeperAddress):
    sender_address = beekeeperAddress
    sender_account = sender_address
    transaction_beekeeper = contract.functions.registerBeekeeper(beekeeperId).build_transaction({
        'from': sender_account,
        'gas': 200000
    })
    transaction_hash_beekeeper = web3.eth.send_transaction(transaction_beekeeper)
    print(f"transaction_beekeeper: {transaction_hash_beekeeper.hex()}")


def register_hive(web3, contract, hive_id, beekeeperId, beekeeperAddress):
    sender_address = beekeeperAddress
    sender_account = sender_address
    transaction_hive = contract.functions.registerHive(hive_id, beekeeperId).build_transaction({
        'from': sender_account,
        'gas': 200000
    })
    transaction_hash_hive = web3.eth.send_transaction(transaction_hive)
    print(f"transaction_hive: {transaction_hash_hive.hex()}")


def process_metadata(web3, contract, hive_id, beekeeperAddress, temperature, humidity, co2, weight, hasPests, hasDiseases):
    sender_address = beekeeperAddress
    sender_account = sender_address
    transaction_metadata = contract.functions.processMetadata(hive_id,temperature,humidity,co2,weight,hasPests,hasDiseases).build_transaction({
        'from': sender_account,
        'gas': 200000
    })
    transaction_hash_metadata = web3.eth.send_transaction(transaction_metadata)
    print(f"transaction_metadata: {transaction_hash_metadata.hex()}")

def send_to_web_page(message):
    global ws_server
    ws_server.send_message_to_all(message)

def start_ws_server():
    global ws_server
    ws_server = WebsocketServer(host='localhost', port=8765)
    ws_server.run_forever()

def main():
     # Start the WebSocket server in a separate thread
    ws_thread = threading.Thread(target=start_ws_server)
    ws_thread.start()
    
    # Connect to Ganache blockchain
    provider = Web3.HTTPProvider("http://127.0.0.1:7545")
    web3 = Web3(provider)

    if web3.is_connected():
        print("Connected to Ganache blockchain!")
    else:
        print("Connection failed. Check the endpoint URL.")

    # Load contract storeHashContract ABI and address
    with open("StoreHashContract.abi", "r") as f:
        contract_abi = f.read()
    contract_address = "0x55911d6D2B22add3ff5f3408a2E2B8D826db53fC"  # Deployed contract address

    # Create contract instance
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    # Set up event filter
    event_filter = contract.events.IPFSHashRetrieved.create_filter(fromBlock='latest')

    while True:
        for event in event_filter.get_new_entries():
         if handle_event(event):
          break  # Exit the loop if handle_event returns False
         
if __name__ == "__main__":
    main()
