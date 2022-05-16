import enum
import json
from os import environ
from unicodedata import decimal
from eth_utils import to_bytes
from web3 import Web3, HTTPProvider
import requests
import logging
import re

evm_logger: logging.Logger = logging.getLogger(name='EVM')
evm_logger.setLevel(logging.DEBUG)

handler: logging.StreamHandler = logging.StreamHandler()
formatter: logging.Formatter = logging.Formatter('[%(name)s] %(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
evm_logger.addHandler(handler)

evm_rpc_url = 

test_wlike =

priv_key = 

test_controller_addr =

class chain(enum.IntEnum):
    mainnet = 1
    ropsten = 3
    rinkeby = 4
    kovan = 42
    hardhat = 31337

chain_id = chain.rinkeby
with open("token.json") as f:
    abi = json.load(f)

w3 = Web3(Web3.HTTPProvider(evm_rpc_url))

from web3.middleware import geth_poa_middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

abi = abi["abi"]

wlike = w3.eth.contract(address=test_wlike, abi=abi)


def mint_wlike(recipient_address,amount,like_txid):
    try:
        transaction = wlike.functions.mint(amount,recipient_address,like_txid).buildTransaction({
            'chainId': chain_id,
            'gas':210000,
            'nonce': w3.eth.getTransactionCount(test_controller_addr)})
        evm_logger.debug("transaction: bulit")
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=priv_key)
        evm_logger.debug("transaction: signed")
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        evm_logger.debug("transaction: sent")
        response = {"status":"success","txid":w3.toHex(txn_hash)}
        evm_logger.info("mint wlike to: {} amount: {} txid: {}".format(recipient_address,amount,w3.toHex(txn_hash)))
        return(response)
    except Exception as e:
        evm_logger.error("transaction error: recipient_address: {} amount: {} like_txid: {}".format(recipient_address,amount,like_txid))
        evm_logger.error("transaction error: {}".format(str(e)))
        response = {"status":"failure","message":str(e)}
        return(response)

def mint_check(txid):
    try:
        record = wlike.functions.mint_status(txid).call()
        if record == True:
            response = {"status":"true"}
            return(response)
        else:
            response = {"status":"false","message":"Transaction not mint."}
            evm_logger.info("hi")
            return(response)
    except Exception as e:
        evm_logger.error("mint check error: txid: {}".format(txid))
        evm_logger.error("mint check error: {}".format(str(e)))
        response = {"status":"failure","message":str(e)}
        return(response)
        
def transaction_check(txid):
    try:
        payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": [txid],
        "id": 1
        })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", evm_rpc_url, headers=headers, data=payload)
    except:
        evm_logger.error("RPC connection error: txid: {}".format(txid))
        response = {"status":"failure","message":"rpc connection error."}

    hash_data = json.loads(response.text)
    
    try:
        if  hash_data["result"] == None:
            response = {"status":"failure","message":"transaction not found or network error."}
            return response

        if hash_data["error"] != None:
            response = {"status":"failure","message":"txid or rpc error."}
            return response
    except:
        pass

    try:
        logs = hash_data['result']['logs']
        recipient_datas = logs[0]["data"][2:]
        amount_datas = logs[1]["data"][2:]
        
        recipient_data = re.findall(r".{64}", recipient_datas)
        amount_data = re.findall(r'.{64}', amount_datas)
        
        try: 
            name = bytes.fromhex(recipient_data[3]).decode().strip("\x00")
            if name != "data":
                recipient_data, amount_data = amount_data, recipient_data
                name = bytes.fromhex(recipient_data[3]).decode().strip("\x00")
        except:
            recipient_data, amount_data = amount_data, recipient_data
            name = bytes.fromhex(recipient_data[3]).decode()
        
        like_amount = int(amount_data[0], 16)
        
        like_amount = like_amount / (10**18)
        
        recipient_address = ""
        for data in recipient_data[5:]:
            temp_data = bytearray.fromhex(data).decode()
            recipient_address += temp_data
        
        recipient_address = recipient_address.strip("\x00")

        evm_logger.debug("like_address: {}".format(recipient_address))

        evm_logger.debug("liker_amount: {}".format(like_amount))
        
    except Exception as e:
        evm_logger.error("transaction check error: txid: {}".format(txid))
        evm_logger.error("transaction check error: {}".format(str(e)))
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
