import traceback
from pymongo import MongoClient
from PIL import Image
import requests
from urllib.request import Request, urlopen  # Python 3
from web3 import Web3
client = MongoClient('mongodb+srv://zkiihne:union557@cluster0-ij9ez.mongodb.net/test?retryWrites=true&w=majority')

from multiprocessing.dummy import Pool as ThreadPool

def get_uri(contract_address, token_id, owner_address, land=True):
    import warnings

    warnings.filterwarnings("ignore", category=DeprecationWarning)



    image_links = []
    total_uri = []
    inputarray = []
    for i in range(0, len(contract_address)):
        inputarray.append([contract_address[i], int(token_id[i]), owner_address, land])
    pool = ThreadPool(len(contract_address))
    # for i in range(0, len(token_id)):
    #     ca = contract_address[i]
    #     ti = int(token_id[i])
    results = pool.map(threadfetch, inputarray)
    for r in results:
        if r != None:
            total_uri.append(r[0])
            image_links.append(r[1])
    return total_uri, image_links

def threadfetch(inp):
    ca = inp[0]
    ti = int(inp[1])
    owner_address = inp[2]
    land = inp[3]
    w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/bfa70a4ec6eb4a69bdd3866b685abfeb"))
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
            'inputs': [{'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}],
            'name': 'uri',
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
    checker = False
    uri = "1"
    try:

        ck_contract = w3.eth.contract(address=w3.toChecksumAddress(ca), abi=simplified_abi)

        try:
            symbol = ck_contract.functions.symbol().call()
        except:
            symbol = ""
        checker = True
        try:
            uri = ck_contract.functions.tokenURI(ti).call()
        except:
            uri = ck_contract.functions.uri(ti).call()
        # name = ck_contract.functions.name().call()
        name = ""
        checker = False
        try:
            owner = ck_contract.functions.ownerOf(ti).call()
        except:
            owner = owner_address
        if owner.lower() == owner_address.lower() or owner_address == "":
            if land:
                if symbol == "LAND":
                    return None
                if "LAND" in name:
                    return None
            # if symbol == "LAND" and land:
            #     return None

            ipfsurl = 'https://ipfs.io/ipfs/'
            if 'ipfs://' in uri:
                uri = ipfsurl + uri.split("ipfs://ipfs/")[1]
            if '{id}' in uri:

                uri = uri[:len(uri)-6] + str(ti)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            x = requests.get(uri, headers=headers)
            xjson = x.json()

            imageurl = x.json().get("image")
            uriresult = None
            imageresult = None

            if 'ipfs://' in imageurl:
                imageurl = ipfsurl + imageurl.split("ipfs://ipfs/")[1]

                try:
                    req = Request(imageurl)
                    req.add_header('User-Agent', headers.get('User-Agent'))
                    image = Image.open(urlopen(req, timeout=5))

                    width, height = image.size
                    xjson["height"] = height
                    xjson["width"] = width
                    xjson["address"] = ca
                    xjson["token_id"] = ti
                    if width == 0 or height == 0:
                        width = width + 1
                        height = height + 1

                    # print(width, height)
                    imageresult = [imageurl, width, height]
                    uriresult = xjson
                except:
                    traceback.print_exc()
            else:
                try:
                    req = Request(imageurl)
                    req.add_header('User-Agent', headers.get('User-Agent'))
                    image = Image.open(urlopen(req, timeout=5))
                    width, height = image.size
                    xjson["height"] = height
                    xjson["width"] = width
                    xjson["address"] = ca
                    xjson["token_id"] = ti
                    if width == 0 or height == 0:
                        width = width + 1
                        height = height + 1

                    # print(width, height)
                    imageresult = [imageurl, width, height]
                    uriresult = xjson
                except:
                    traceback.print_exc()

            if uriresult != None:
                return [uriresult, imageresult]
            else:
                pass
                # print("no result")
    except:
        # print(checker, uri, ca, ti)
        traceback.print_exc()
        # pass

def create_object(client, object_name, collection_name, info, key):
    db = client[object_name]
    db[collection_name].update(key ,info, upsert=True)

def insert_object(client, object_name, collection_name, info,):
    db = client[object_name]
    result = db[collection_name].insert_one(info)


def delete_collection(client, object_name, collection_name):
    db = client[object_name]
    db[collection_name].delete_many()

def update_object(client, object_name, collection_name, id, update_dict):
    db = client[object_name]
    db[collection_name].update({"_id":id},{"$set":update_dict})

def find_one( collection, table,  address, token_id):
    db = client[collection]
    object = db[table].find_one({"address": address, "token_id": str(token_id)})
    print(object)
    return object
def find_nft(address, token_id):
    collection = 'NFTGallery'
    table = 'nft'
    db = client[collection]
    object = db[table].find_one({"address": address, "token_id": str(token_id)})
    print("--", address, token_id, bool(object))
    return object

def find_user(address):
    collection = 'NFTGallery'
    table = 'users'
    db = client[collection]
    object = db[table].find_one({"address": address})
    print(object)
    return object

# GET user
def get_user_gallery(user_address):
    gallery = find_user(user_address).get('gallery')
    uriarray = []
    imagearray = []
    for g in gallery:
        address = g.get("address")
        token_id = g.get("token_id")
        nft = find_nft(address, token_id)
        if nft == None:
            nft = threadfetch([address, token_id, "", False])
        else:
            nft = format_nft(nft)
        if nft != None:
            uriarray.append(nft[0])
            imagearray.append(nft[1])
    return uriarray, imagearray

# helper
def format_nft(nft):
    nft = [nft.get("uri"), [nft.get('image'), nft.get("uri").get('height'), nft.get("uri").get('width')]]
    return nft

# GET global
def get_global_gallery():
    collection = 'NFTGallery'
    table = 'globalgallery'
    db = client[collection]
    gallery = db[table].find({})
    uriarray = []
    imagearray = []

    for g in gallery:
        address = g.get("address")
        token_id = g.get("token_id")
        nft = find_nft(address, token_id)
        if nft == None:
            nft = threadfetch([address, token_id, "", False])
        else:
            nft = format_nft(nft)
        uriarray.append(nft[0])
        imagearray.append(nft[1])
    return uriarray, imagearray

# POST global
def create_nft(address, token_id):

    inp = threadfetch([address, token_id, "", False])
    print(inp)
    # inp = input[0]
    uri = inp[0]
    image = inp[1][0]
    points = 0
    ranking_points = points + 1500
    contract_address = inp[0].get('contract_address')
    token_id = inp[0].get("token_id")
    # print(image, contract_address, token_id)
    nftinput = {'uri': uri, 'image': image, 'token_id':str(token_id), 'address': address,"points": points }
    galleryinput = {'token_id': token_id, 'address': address, "ranking_points": ranking_points}

    collection = 'NFTGallery'
    table = 'nft'
    db = client[collection]
    # db[table].insert_one( nftinput)
    db[table].update_one({"address": address, "token_id": str(token_id)}, {"$set": nftinput}, upsert=True)

    collection = 'NFTGallery'
    table = 'globalgallery'
    db = client[collection]
    db[table].update_one({"address": address, "token_id": str(token_id)}, {"$set": galleryinput}, upsert=True)

# POST user
def add_to_gallery(user, address, token_id):
    collection = 'NFTGallery'
    table = 'users'
    db = client[collection]
    db[table].update_one({"address": user}, {"$push": {'gallery': {'address':address, 'token_id':str(token_id)}}}, upsert=True)
    table = 'latest'
    inlatest = db[table].find_one({"address": address, "token_id":str(token_id)})
    print(">>-", address, token_id, inlatest)
    if inlatest:
        table = 'nft'
        nftinput = {'uri': inlatest["uri"], 'image': inlatest["image"], 'token_id': inlatest["token_id"],
                    'address': inlatest["address"], "points": inlatest["points"]}
        db[table].update_one({"address": address, "token_id": str(token_id)}, {"$set": nftinput}, upsert=True)

# DELETE user
def remove_from_gallery(user, address, token_id):
    collection = 'NFTGallery'
    table = 'users'
    db = client[collection]
    db[table].update_one({"address": user}, {"$pull": {'gallery': {'address':address, 'token_id':str(token_id)}}})

# retrieve contents of latest gallery
def get_latest_gallery():
    collection = 'NFTGallery'
    table = 'latest'
    db = client[collection]
    gallery = db[table].find({})
    uriarray = []
    imagearray = []

    for g in gallery:
        address = g.get("address")
        token_id = g.get("token_id")

        nft = format_nft(g)
        print(nft)
        uriarray.append(nft[0])
        imagearray.append(nft[1])
    return uriarray, imagearray

# helper to get latest NFT from opensea
def get_latest_opensea(marker=0):
    contracts = []
    tokenids = []
    api_url = "https://api.opensea.io/api/v1/events?only_opensea=false&offset=" + str(marker) +"&limit=2000"
    x = requests.get(api_url)
    jsun = x.json()
    try:
        events = jsun["asset_events"]
    except:
        events = []
    for e in events:

        if e["asset"] != None:
            tid = e["asset"]["token_id"]
            ca = e["asset"]["asset_contract"]["address"]
            contracts.append(ca)
            tokenids.append(tid)
        else:
            print(e)

    return contracts, tokenids


# function to add to the latest gallery
def job_function():
    collection = 'NFTGallery'
    table = 'latest'
    db = client[collection]
    # erase lastest in db

    # get latest from opensea -> get 2k at a time, fill in valid ones until you have 2000
    results_contracts = []
    results_tokens = []
    marker = 0
    while len(results_contracts) < 200:
        contracts, tokens = get_latest_opensea(marker)
        if len(contracts) == 0:
            break
        uri, image_links = get_uri(contracts, tokens, "", land=False)
        for i in range(len(uri)):
            results_contracts.append(uri[i])
            results_tokens.append(image_links[i])


        marker = marker + 2000

    # put into database
    insert_input = []
    for rc in results_contracts:
        rc['token_id'] = str(rc["token_id"])
        image = rc.get("image")
        token_id = rc.get("token_id")
        address = rc.get("address")
        points = 0
        nftinput = {'uri': rc, 'image': image, 'token_id': token_id, 'address': address, "points": points}
        insert_input.append(nftinput)
    if len(insert_input) > 0:
        db[table].delete_many({})
        db[table].insert_many(insert_input)
    else:
        print("none")
    print("going at it")

if __name__ == "__main__":
    # r = threadfetch(["0x50f5474724e0ee42d9a4e711ccfb275809fd6d4a", 100151,"", False])
    # print(r)

    # collection = 'NFTGallery'
    # db = client[collection]
    # table = 'latest'
    # address = "0x495f947276749ce646f68ac8c248420045cb7b5e"
    # token_id = "28536019139059307169089330544806946670165581714995785789713468549246918590465"
    # inlatest = db[table].find_one({"address": address, "token_id": token_id})
    # inlatest.pop("_id", None)
    # print(inlatest)
    # if inlatest:
    #     table = 'nft'
    #     nftinput = {'uri': inlatest["uri"], 'image': inlatest["image"], 'token_id': inlatest["token_id"], 'address': inlatest["address"], "points": inlatest["points"]}
    #     db[table].update_one({"address": address, "token_id":token_id}, {"$set": nftinput}, upsert=True)
    #     print("done!")
    job_function()
    # pass
    # get_latest_gallery()
    # w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/bfa70a4ec6eb4a69bdd3866b685abfeb"))
    # address = '0x60f80121c31a0d46b5279700f9df786054aa5ee5'
    # abi = [
    #     {
    #         "inputs": [],
    #         "name": "name",
    #         "outputs": [{"internal_type": "string", "name": "", "type": "string"}],
    #         "state_mutability": "view", "type": "function", "constant": True
    #     }]
    # contract_instance = w3.eth.contract(address=w3.toChecksumAddress(address), abi=abi)
    #
    # # read state:
    # contract_instance.functions.name().call()

    # remove_from_gallery('0xebedeef778d98695cf427ec0d37aebe6ee8de927', '0x60f80121c31a0d46b5279700f9df786054aa5ee5', 260853)
    # add_to_gallery( '0xebedeef778d98695cf427ec0d37aebe6ee8de927','0x60f80121c31a0d46b5279700f9df786054aa5ee5' ,260853 )
    # sf
    # # find_nft('0x60f80121c31a0d46b5279700f9df786054aa5ee5', 236123)
    # for g in get_user_gallery('0xebedeef778d98695cf427ec0d37aebe6ee8de927'):
    #     print("g", g)
    # asdf
    # print(get_global_gallery())
    # sdf
    # input = [{'name': 'hvmble#boi', 'description': 'Head: Iridescent Glass\nEyes: Missing\nNose: Iridescent Glass\nMouth: Missing\nBust: Iridescent Glass\nBackdrop: Black\nSeries: Honors (03)\n#: 03', 'image': 'ipfs://ipfs/QmTXqUM3ohHYRadTs9ESy1sZ9rFSenZrLCSZ4VaYonsZTz/image.jpeg', 'external_url': 'https://app.rarible.com/token/0x60f80121c31a0d46b5279700f9df786054aa5ee5:260853', 'attributes': [], 'height': 2000, 'width': 2000, 'contract_address': '0x60f80121c31a0d46b5279700f9df786054aa5ee5', 'token_id': 260853}, ['https://ipfs.io/ipfs/QmTXqUM3ohHYRadTs9ESy1sZ9rFSenZrLCSZ4VaYonsZTz/image.jpeg', 2000, 2000]],
    # create_nft('0x60f80121c31a0d46b5279700f9df786054aa5ee5', 260853)
    # formatting
    # insert into global
    # insert into user
    # inser user
