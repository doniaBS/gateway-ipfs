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
        return False
    else:
        error_message = "Failed to retrieve metadata from IPFS. Data has been changed"
        error_message_json = json.dumps( error_message)
        print( error_message_json)
        # Send the error message to the web page
        send_to_web_page( error_message_json)
        return False  # Ensure to return False for error case as well

def send_to_web_page(message):
    global ws_server
    ws_server.send_message_to_all(message)
    print(f"Sent to WebSocket: {message}")

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
    contract_address = "0x68922314EF9a987655164d49Cf6B2952CbA5f5bE"  # Deployed contract address

    # Load contract BekeeperContract ABI and address
    with open("BeekeeperContract.abi", "r") as f:
        beekeeperContract_abi = f.read()
    beekeeperContract_address = "0xa8C5e5189614ac9Ea601b923F284dB6283C26732"  # Deployed contract address

    # Create contract instance
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    # Create contract instance
    contractBeekeeper = web3.eth.contract(address=beekeeperContract_address, abi=beekeeperContract_abi)

    # Set up event filter
    event_filter = contract.events.IPFSHashRetrieved.create_filter(fromBlock='latest')

    while True:
        for event in event_filter.get_new_entries():
         if not handle_event(event):
          break  # Exit the loop if handle_event returns False

if __name__ == "__main__":
    main()
