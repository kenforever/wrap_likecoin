import enum
import json
from os import environ
from unicodedata import decimal
from eth_utils import to_bytes
import web3
from web3 import Web3, HTTPProvider
import requests
import logging
import re
from google.cloud import secretmanager
import os
import logging.handlers


# wlike_logger: logging.Logger = logging.getLogger(name='EVM')
# wlike_logger.setLevel(logging.DEBUG)

# handler: logging.StreamHandler = logging.StreamHandler()
# formatter: logging.Formatter = logging.Formatter('[%(name)s] %(asctime)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# wlike_logger.addHandler(handler)


wlike_logger: logging.Logger = logging.getLogger(name='wlike')
wlike_logger.setLevel(logging.DEBUG)
log_dir = "logs/wlike"
timefilehandler = logging.handlers.TimedRotatingFileHandler(
    log_dir + os.sep +"wlike",
    when="D",
    interval=1,
    backupCount=20
)
timefilehandler.suffix = "%Y-%m-%d_%H-%M-%S.log"
formatter: logging.Formatter = logging.Formatter('[%(name)s] %(asctime)s - %(levelname)s - %(message)s')
timefilehandler.setFormatter(formatter)
wlike_logger.addHandler(timefilehandler)

# get secret from secret manager
# rpc
project_id = "wrap-like-dev"
INFURA_RINKEBY_RPC_SECRET_ID = "infura_rinkeby_rpc"
client = secretmanager.SecretManagerServiceClient()
parent = f"projects/{project_id}"
INFURA_RINKEBY_RPC_SECRET_LOCATE = f"{parent}/secrets/{INFURA_RINKEBY_RPC_SECRET_ID}/versions/latest"
INFURA_RINKEBY_RPC_SECRET_RESPONSE = client.access_secret_version(request={"name": INFURA_RINKEBY_RPC_SECRET_LOCATE})
INFURA_RINKEBY_RPC_SECRET = INFURA_RINKEBY_RPC_SECRET_RESPONSE.payload.data.decode("UTF-8")
# controller
WLIKE_CONTROLLER_PRIV_KEY_ID = "wlike_controller_priv_key"
WLIKE_CONTROLLER_PRIV_KEY_LOCATE = f"{parent}/secrets/{WLIKE_CONTROLLER_PRIV_KEY_ID}/versions/latest"
WLIKE_CONTROLLER_PRIV_KEY_RESPONSE = client.access_secret_version(request={"name": WLIKE_CONTROLLER_PRIV_KEY_LOCATE})
WLIKE_CONTROLLER_PRIV_KEY = WLIKE_CONTROLLER_PRIV_KEY_RESPONSE.payload.data.decode("UTF-8")

test_wlike = "0x5A9Ed15Bb303bca3F814710466eb53B31e5AA48c"

test_controller_addr = "0x1A89Fcebc7B13290a8568323AFE7B0243E6Ed076"

class chain(enum.IntEnum):
    mainnet = 1
    ropsten = 3
    rinkeby = 4
    kovan = 42
    hardhat = 31337

chain_id = chain.rinkeby
# web3py init and abi setting
with open("token.json") as f:
    abi = json.load(f)
w3 = Web3(Web3.HTTPProvider(INFURA_RINKEBY_RPC_SECRET))
from web3.middleware import geth_poa_middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
abi = abi["abi"]
wlike = w3.eth.contract(address=test_wlike, abi=abi)


# mint wlike 
# this function will not check the transaction status.
# this will mint wlike directly. 
def mint_wlike(recipient_address,amount,like_txid):
    try:
        # build transaction
        transaction = wlike.functions.mint(amount,recipient_address,like_txid).buildTransaction({
            'chainId': chain_id,
            'gas':210000,
            'nonce': w3.eth.getTransactionCount(test_controller_addr)})
        wlike_logger.debug("transaction: bulit")
        # sign transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=WLIKE_CONTROLLER_PRIV_KEY)
        wlike_logger.debug("transaction: signed")
        # send transaction and get txid
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        wlike_logger.debug("transaction: sent")
        # return txid
        response = {"status":"success","txid":w3.toHex(txn_hash)}
        wlike_logger.info("mint wlike to: {} amount: {} txid: {}".format(recipient_address,amount,w3.toHex(txn_hash)))
        return(response)
    except Exception as e:
        wlike_logger.error("transaction error: recipient_address: {} amount: {} like_txid: {}".format(recipient_address,amount,like_txid))
        wlike_logger.error("transaction error: {}".format(str(e)))
        response = {"status":"failure","message":str(e)}
        return(response)

def mint_check(txid):
    try:
        # call mint_status function on wlike contract
        # to check if the transaction is minted or not
        # on evm side, the mint status is stored on chain
        # not on mongoDB.
        record = wlike.functions.mint_status(txid).call()
        if record == True:
            response = {"status":"true"}
            return(response)
        else:
            response = {"status":"false","message":"Transaction not mint."}
            wlike_logger.info("hi")
            return(response)
    except Exception as e:
        wlike_logger.error("mint check error: txid: {}".format(txid))
        wlike_logger.error("mint check error: {}".format(str(e)))
        response = {"status":"failure","message":str(e)}
        return(response)

# get transaction data from evm via rpc
# not using web3py because it is not supported well
# we shoult get the recipient address and like amount from the transaction data.       
def transaction_check(txid):
    try:
        # get transaction data from evm via rpc
        payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": [txid],
        "id": 1
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", INFURA_RINKEBY_RPC_SECRET, headers=headers, data=payload)
    except:
        wlike_logger.error("RPC connection error: txid: {}".format(txid))
        response = {"status":"failure","message":"rpc connection error."}

    hash_data = json.loads(response.text)
    
    # if the hash_data['result'] is empty, it means the transaction not found.
    # probably the transaction id is wrong.
    # or the rpc is not working. 

    # if the hash_data['error'] is not empty, it means the transaction esists 
    # but it got an error, so this transaction is illegal.
    try:
        if  hash_data["result"] == None:
            response = {"status":"failure","message":"transaction not found or network error."}
            return response

        if hash_data["error"] != None:
            response = {"status":"failure","message":"txid or rpc error."}
            return response
    except:
        pass

    # the data we need is stored in the hash_data['result']['logs']
    # they are stored in hex format. we need to convert them to string.
    # the '0x' is unnecessary. we need to remove it.
    try:
        logs = hash_data['result']['logs']
        recipient_datas = logs[0]["data"][2:]
        amount_datas = logs[1]["data"][2:]
        
        recipient_data = re.findall(r".{64}", recipient_datas)
        amount_data = re.findall(r'.{64}', amount_datas)
        
        # we stored a "data" in the recipient address part.
        # so if the data dont have a 'data' it mean it probably is the amount data.
        try: 
            name = bytes.fromhex(recipient_data[3]).decode().strip("\x00")
            if name != "data":
                recipient_data, amount_data = amount_data, recipient_data
                name = bytes.fromhex(recipient_data[3]).decode().strip("\x00")
        except:
            recipient_data, amount_data = amount_data, recipient_data
            name = bytes.fromhex(recipient_data[3]).decode()
        
        # we got 
        like_amount = int(amount_data[0], 16)
        
        like_amount = like_amount / (10**18)
        
        recipient_address = ""
        for data in recipient_data[5:]:
            temp_data = bytearray.fromhex(data).decode()
            recipient_address += temp_data
        
        recipient_address = recipient_address.strip("\x00")

        wlike_logger.debug("like_address: {}".format(recipient_address))

        wlike_logger.debug("liker_amount: {}".format(like_amount))
        
    except Exception as e:
        wlike_logger.error("transaction check error: txid: {}".format(txid))
        wlike_logger.error("transaction check error: {}".format(str(e)))
        response = {"status":"failure","message":"transaction format not corect. did you provide correct txid?"}
        return(response)
    
    status = hash_data["result"]["status"]
    to = hash_data["result"]["to"]
    #from_address = hash_data["result"]["from"]

    if status != "0x1" :
        response = {"status":"failure","message":"transaction fail."}
        return response
    if to.lower() != test_wlike.lower():
        response = {"status":"failure","message":"contract address mismatch."}
        return response
    # if from_address != evm_address:
    #     response = {"status":"failure","message":"address mismatch."}
    #     return response

    response = {"status":"success","recipient":recipient_address,"amount":like_amount}
    return response


def logging_test():
    wlike_logger.info("hi")
    wlike_logger.error("hi")
    wlike_logger.debug("hi")
    wlike_logger.warning("hi")
    wlike_logger.critical("hi")