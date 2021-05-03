from graphene import ObjectType, String, Boolean, ID, Field, Int,List , Float, JSONString

import json

import pandas as pd

from random import randrange
from dblayer import *



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

class Nulltype(ObjectType):
    result = Boolean()

class Query(ObjectType):
    vp = List(NFTS, wa=String())
    getglobalgallery = List(NFTS)
    getlatestgallery = List(NFTS)
    getusergallery = List(NFTS, wa=String())
    globalnfts = List(NFTS)
    random = List(NFTS)
    addtoglobal = List(Boolean,  wa=String(), tkid=String())
    addtousergallery = List(Boolean,  us=String(), wa=String(), tkid=String())
    removefromusergallery = List(Boolean, us=String(), wa=String(), tkid=String())
    def resolve_vp(self, info, wa):
        contract_address, token_id = get_address(wa)
        uri, image_links = get_uri(contract_address, token_id, wa)
        stuff = {"uri": uri, "address": wa, "images": image_links, "owner": "You"}
        return [stuff]

    def resolve_random(self, info):

        # contract_address, token_id, owner_address, owner = get_random_address()
        contract_address, token_id = get_latest_opensea()
        uri, image_links = get_uri(contract_address, token_id, "")

        stuff = {"uri": uri, "address": "", "images": image_links, "name": "" }
        return [stuff]


    def resolve_getglobalgallery(self, info):

        uri, image_links = get_global_gallery()
        print(uri)
        print(image_links)
        stuff = {"uri": uri, "address": "Global", "images": image_links, "owner": "Users"}
        return [stuff]

    def resolve_getusergallery(self, info, wa):

        uri, image_links = get_user_gallery(wa)
        stuff = {"uri": uri, "address": wa, "images": image_links, "owner": wa}
        return [stuff]
    def resolve_addtoglobal(self, info, wa, tkid):
        print(wa, tkid)
        tkid = int(tkid)
        create_nft(wa, tkid)
        return [True]
    def resolve_addtousergallery(self, info, us, wa, tkid):
        print(us, wa, tkid)
        tkid = int(tkid)
        add_to_gallery(us, wa, tkid)
        return [True]

    def resolve_removefromusergallery(self, info, us, wa, tkid):
        print(us, wa, tkid)
        tkid = int(tkid)
        remove_from_gallery(us, wa, tkid)
        return [True]

    def resolve_getlatestgallery(self, info):
        uri, images = get_latest_gallery()
        stuff = {"uri": uri, "address": "Global", "images": images, "owner": "Users"}
        return [stuff]


if __name__ == "__main__":

    contract_address, token_id = get_latest_opensea()
    uri, image_links = get_uri(contract_address, token_id, "")
    print(uri)
    print(image_links)
    # contract_address, token_id = get_latest_opensea()
    # print(contract_address, token_id)
    # # inp = ['0x60f80121c31a0d46b5279700f9df786054aa5ee5', "236123", ""]
    # for i in range(0, len(contract_address)):
    #     inp = [contract_address[i], token_id[i], ""]
    #     try:
    #         t = threadfetch(inp)
    #         print(t)
    #     except:
    #         traceback.print_exc()
    # uri, image_links = get_uri2(contract_address, token_id, "")
    # print(uri, image_links)


    # df = pd.read_csv('myfile.csv')
    # addresses = df['Address'].values.tolist()
    # tokens = df['Token'].values.tolist()
    # uri, image_links = get_uri(['0x60f80121c31a0d46b5279700f9df786054aa5ee5'], [57201], "")

    # df = pd.read_csv('data.csv')
    #
    # allcontracts = []
    # alltokens = []
    # for index, row in df.iterrows():
    #     address = row['Address']
    #     with open('key.json', mode='r') as key_file:
    #         key = json.loads(key_file.read())['key']
    #     api_url = "https://api.etherscan.io/api?module=account&action=tokennfttx&address=" + address + "&startblock=0&endblock=999999999&sort=asc&apikey=" + key
    #     print(api_url)
    #     x = requests.get(api_url)
    #     print(x.json())
    #     alltransactions = x.json().get("result")
    #     contracts = []
    #     ids = []
    #     for t in alltransactions:
    #         if t.get("to") == address:
    #             # print(t)
    #             contract_address = t.get("contractAddress")
    #             token_id = t.get("tokenID")
    #             # print(contract_address, token_id)
    #             contracts.append(contract_address)
    #             ids.append(int(token_id))
    #     print("//", contracts)
    #     print("///", ids)
    #     allcontracts.append(contracts)
    #     alltokens.append(ids)
    #     print("//", allcontracts)
    #     print("///", alltokens)
    #     # allcontracts = [item for sublist in allcontracts for item in sublist]
    #     # alltokens = [item for sublist in alltokens for item in sublist]
    #     # print(allcontracts, alltokens)
    # allcontracts = [item for sublist in allcontracts for item in sublist]
    # alltokens = [item for sublist in alltokens for item in sublist]
    # # pd.DataFrame(data=np.array([allcontracts, alltokens]), columns = ['Address', 'Token'])
    # df = pd.DataFrame({'Address': allcontracts, 'Token': alltokens})
    # df.to_csv('myfile.csv')

    # contract_address, token_id, owner_address, name = get_random_address()
    # uri, image_links = get_uri(contract_address, token_id, owner_address)
    # print(type(uri), type(uri[0]))
    # stuff = {"uri": uri, "address": owner_address, "images": image_links, "owner": name}
    # print(stuff)
    #
    # # mark cubans address
    # # 0xa679c6154b8d4619af9f83f0bf9a13a680e01ecf
    # wallet_address = '0xa679c6154b8d4619af9f83f0bf9a13a680e01ecf'
    # contract_address, token_id = get_address(wallet_address)
    # uri = get_uri(contract_address, token_id, wallet_address)
    # print(uri)
