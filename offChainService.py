import json
import requests
from web3 import Web3

def handle_event(event):
    beekeeper_address = event['args']['beekeeperAddress']
    ipfs_hash = event['args']['retrievedHash']
    print(f"Received IPFS hash: {ipfs_hash} for beekeeper address: {beekeeper_address}")

    # Construct the request URL
    pinata_gateway = 'https://api.pinata.cloud/data/pinList'
    request_url = f"{pinata_gateway}{ipfs_hash}"

    # Make the HTTP request to IPFS
    response = requests.get(request_url)
    if response.status_code == 200:
        metadata = response.json()
        print(f"Retrieved metadata: {metadata}")
        # Send the metadata to the BeekeeperContract or handle it as needed
    else:
        print(f"Failed to retrieve metadata from IPFS. Status code: {response.status_code}")

def main():
    # Connect to Ganache blockchain
    provider = Web3.HTTPProvider("http://127.0.0.1:7545")
    web3 = Web3(provider)

    if web3.is_connected():
        print("Connected to Ganache blockchain!")
    else:
        print("Connection failed. Check the endpoint URL.")

    # Load contract ABI and address
    with open("StoreHashContract.abi", "r") as f:
        contract_abi = f.read()
    contract_address = "0x87A29eD0569dbffe557F64c784606db4d3796693"  # Deployed contract address

    # Create contract instance
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    # Set up event filter
    event_filter = contract.events.IPFSHashRetrieved.create_filter(fromBlock='latest')

    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)

if __name__ == "__main__":
    main()
