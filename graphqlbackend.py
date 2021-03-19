from graphene import ObjectType, String, Boolean, ID, Field, Int,List , Float, JSONString
import urllib.request
from PIL import Image
import json
import requests

# helper to actually fetch the NFTs of a wallet
def get_uri(contract_address, token_id, owner_address):
    import warnings

    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider("https://cloudflare-eth.com"))

    simplified_abi = [
        {
            'inputs': [{'internalType': 'address', 'name': 'owner', 'type': 'address'}],
            'name': 'balanceOf',
            'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
            'payable': False, 'stateMutability': 'view', 'type': 'function', 'constant': True
        },
        {
            'inputs': [],
            'name': 'name',
            'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
            'stateMutability': 'view', 'type': 'function', 'constant': True
        },
        {
            'inputs': [{'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}],
            'name': 'ownerOf',
            'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
            'payable': False, 'stateMutability': 'view', 'type': 'function', 'constant': True
        },
        {
            'inputs': [{'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}],
            'name': 'tokenURI',
            'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
            'payable': False, 'stateMutability': 'view', 'type': 'function', 'constant': True
        },
        {
            'inputs': [],
            'name': 'symbol',
            'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
            'stateMutability': 'view', 'type': 'function', 'constant': True
        },
        {
            'inputs': [],
            'name': 'totalSupply',
            'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
            'stateMutability': 'view', 'type': 'function', 'constant': True
        },
    ]

    
    image_links = []
    total_uri = []
    for i in range(0, len(token_id)):
        ca = contract_address[i]
        ti = token_id[i]
        ck_contract = w3.eth.contract(address=w3.toChecksumAddress(ca), abi=simplified_abi + ck_extra_abi)
        try:
            name = ck_contract.functions.name().call()
            symbol = ck_contract.functions.symbol().call()
            uri = ck_contract.functions.tokenURI(ti).call()
            owner = ck_contract.functions.ownerOf(ti).call()
            print(name, symbol, owner, uri)

            if owner.lower() == owner_address.lower():
                x = requests.get(uri)
                # print(x.json())
                ipfsurl = 'https://ipfs.io/ipfs/'
                imageurl = x.json().get("image")
                if 'ipfs://' in imageurl:
                    imageurl = ipfsurl + imageurl.split("ipfs://ipfs/")[1]

                    try:
                        image = Image.open(urllib.request.urlopen(imageurl, timeout=0.5))
                        width, height = image.size
                        width = int(width / 1000)
                        height = int(height / 1000)
                        if width == 0 or height == 0:
                            width = width + 1
                            height = height + 1

                        # print(width, height)
                        image_links.append([imageurl, width, height])
                        total_uri.append(x.json())
                    except Exception as e:
                        print(e)
                else:
                    try:
                        image = Image.open(urllib.request.urlopen(imageurl, timeout=0.5))
                        width, height = image.size
                        width = int(width/1000)
                        height = int(height / 1000)
                        if width == 0 or height == 0:
                            width = width +1
                            height = height +1

                        # print(width, height)
                        image_links.append([imageurl, width, height])
                        total_uri.append(x.json())
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)
    return total_uri, image_links

# gets all NFTs for a given address
def get_address(address):
    with open('key.json', mode='r') as key_file:
        key = json.loads(key_file.read())['key']
    api_url = "https://api.etherscan.io/api?module=account&action=tokennfttx&address=" + address + "&startblock=0&endblock=999999999&sort=asc&apikey=" + key

    x = requests.get(api_url)
    alltransactions = x.json().get("result")
    contracts = []
    ids = []
    print("all", address, alltransactions)
    for t in alltransactions:

        if t.get("to") == address:
            # print(t)
            contract_address = t.get("contractAddress")
            token_id = t.get("tokenID")
            # print(contract_address, token_id)
            contracts.append(contract_address)
            ids.append(int(token_id))
    return contracts, ids

# helper for get_random_address
def fetch_random():
    import pandas as pd
    from random import randrange
    df = pd.read_csv('data.csv')
    df = df.values.tolist()
    row = df[randrange(len(df))]
    owner = row[0]
    address = row[1]
    print("1", address, len(address), owner)
    return address, owner

# fetches a random address from file of known addresses
def get_random_address():
    address, owner = fetch_random()
    with open('key.json', mode='r') as key_file:
        key = json.loads(key_file.read())['key']
    api_url = "https://api.etherscan.io/api?module=account&action=tokennfttx&address=" + address + "&startblock=0&endblock=999999999&sort=asc&apikey=" + key
    print(api_url)
    x = requests.get(api_url)
    print(x.json())
    alltransactions = x.json().get("result")
    contracts = []
    ids = []
    for t in alltransactions:
        if t.get("to") == address:
            # print(t)
            contract_address = t.get("contractAddress")
            token_id = t.get("tokenID")
            # print(contract_address, token_id)
            contracts.append(contract_address)
            ids.append(int(token_id))
    return contracts, ids, address, owner

class NFTS(ObjectType):
    uri = List(JSONString)
    address = String()
    images = List(String)
    name = String()

class Query(ObjectType):
    vp = List(NFTS, wa=String())
    random = List(NFTS)
    def resolve_vp(self, info, wa):
        contract_address, token_id = get_address(wa)
        uri, image_links = get_uri(contract_address, token_id, wa)
        stuff = {"uri": uri, "address": wa, "images": image_links, "owner": "You"}
        return [stuff]

    def resolve_random(self, info):
        contract_address, token_id, owner_address, owner = get_random_address()
        uri, image_links = get_uri(contract_address, token_id, owner_address)
        print(type(uri), type(uri[0]))
        stuff = {"uri": uri, "address": owner_address, "images": image_links, "name": owner }
        return [stuff]


if __name__ == "__main__":

    contract_address, token_id, owner_address, name = get_random_address()
    uri, image_links = get_uri(contract_address, token_id, owner_address)
    print(type(uri), type(uri[0]))
    stuff = {"uri": uri, "address": owner_address, "images": image_links, "owner": name}
    print(stuff)

    # mark cubans address
    # 0xa679c6154b8d4619af9f83f0bf9a13a680e01ecf
    wallet_address = '0xa679c6154b8d4619af9f83f0bf9a13a680e01ecf'
    contract_address, token_id = get_address(wallet_address)
    uri = get_uri(contract_address, token_id, wallet_address)
    print(uri)
