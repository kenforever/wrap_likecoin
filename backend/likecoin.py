import json
import requests
import logging
import subprocess
import database
import pymongo
from google.cloud import secretmanager
import logging.handlers
import os

from cosmpy.aerial.wallet import LocalWallet
from cosmpy.crypto.keypairs import PrivateKey
from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.aerial.tx import Transaction
from cosmpy.aerial.client.bank import create_bank_send_msg
from cosmpy.aerial.client.utils import prepare_and_broadcast_basic_transaction

likecoin_logger: logging.Logger = logging.getLogger(name='likecoin')
likecoin_logger.setLevel(logging.DEBUG)
log_dir = "logs/likecoin"
timefilehandler = logging.handlers.TimedRotatingFileHandler(
    log_dir + os.sep +"likecoin",
    when="D",
    interval=1,
    backupCount=20
)
timefilehandler.suffix = "%Y-%m-%d_%H-%M-%S.log"
formatter: logging.Formatter = logging.Formatter('[%(name)s] %(asctime)s - %(levelname)s - %(message)s')
timefilehandler.setFormatter(formatter)
likecoin_logger.addHandler(timefilehandler)

# get secret from secret manager
# mongodb url
MONGODB_URL_ID = "mongodb_url"
project_id = "wrap-like-dev"
client = secretmanager.SecretManagerServiceClient()
parent = f"projects/{project_id}"
MONGODB_URL_LOCATE = f"{parent}/secrets/{MONGODB_URL_ID}/versions/latest"
MONGODB_URL_RESPONSE = client.access_secret_version(request={"name": MONGODB_URL_LOCATE})
MONGODB_URL = MONGODB_URL_RESPONSE.payload.data.decode("UTF-8")

#vault privkey
VAULT_PRIVKEY_ID = "vault_privkey"
VAULT_PRIVKEY_LOCATE = f"{parent}/secrets/vault_privkey/versions/latest"
VAULT_PRIVKEY_RESPONSE = client.access_secret_version(request={"name": VAULT_PRIVKEY_LOCATE })
VAULT_PRIVKEY = VAULT_PRIVKEY_RESPONSE.payload.data.decode("UTF-8")

testnet_config = NetworkConfig(
    chain_id="likecoin-public-testnet-5",
    url="rest+https://node.testnet.like.co:443",
    fee_minimum_gas_price=1,
    fee_denomination="nanoekil",
    staking_denomination="nanoekil",
)
testnet_client = LedgerClient(testnet_config)
private_key = PrivateKey(VAULT_PRIVKEY)
wallet = LocalWallet(private_key, prefix="like")
fee_collecter_address = 'like1ehy54c765lfyqrpurrtdsssks30gsjx9txzh2x'


like_main_rpc_url = "https://node.testnet.like.co/"
wlike_vault_address = "like1ehy54c765lfyqrpurrtdsssks30gsjx9txzh2x"

def transaction_check(txid):
    tx = requests.get(like_main_rpc_url + "txs/"+ txid)

    # check rpc response
    if tx.status_code != requests.codes.ok:
        likecoin_logger.error("likecoin rpc error.")
        response = {"status":"failure","message":"transaction not found or network error."}
        return response

    tx_data = json.loads(tx.text)
    # try:
    #     log_data = json.loads(tx_data["raw_log"])
    # except:
    #     response = {"status":"failure","message":"transaction data error."}
    #     return response

    #x check if the transaction is success or not
    try:
        error_code = tx_data["code"]
        response = {"status":"failure","message":"this transaction did not success."}
        return response
    except:
        pass
    
    # check if the transaction memo have any recipient address
    try:
        tx_data = tx_data["tx"]["value"]
        to_address = tx_data["msg"][0]["value"]["to_address"]
    except:
        response = {"status":"failure","message":"the memo did not have any recipient."}
        return response

    amount = tx_data["msg"][0]["value"]["amount"][0]["amount"]
    amount = float(amount) * 0.000000001
    
    recipient_evm = tx_data["memo"]

    if to_address != wlike_vault_address:
       response = {"status":"failure","message":"the recipient of this transaction is not likecoin receiver."}
       return response

    return {"status":"success","recipient":recipient_evm,"amount":amount}


# this will send amount of likecoin to recipient_address
# amount should be in nanolike not like
def send_like( _recipient : str, _amount : int, _txid_evm : str):

    try:
        _fee = int((_amount / 10000) * 500)
        _amount = _amount - _fee
        tx = Transaction()

        tx.add_message(
            create_bank_send_msg(
                from_address=wallet.address(), 
                to_address=_recipient, 
                amount=_amount, 
                denom="nanoekil")
        )

        #fee
        tx.add_message(
            create_bank_send_msg(
                from_address=wallet.address(), 
                to_address=fee_collecter_address, 
                amount=_fee, 
                denom="nanoekil")
        )

        tx = prepare_and_broadcast_basic_transaction(
            client = testnet_client, 
            tx = tx, 
            sender = wallet,
            memo = _txid_evm)
        
        tx_hash = tx.tx_hash

        database.add_tx_evm_to_like(
            to_contract_txid=_txid_evm,
            from_vault_txid=tx_hash,
            like_address=_recipient, 
            amount=_amount)

        tx.wait_to_complete()

        

        database.update_tx_status_evm_to_like(
            to_contract_txid=_txid_evm,
            status="finish"
        )

        likecoin_logger.info("ekil send: txid: "+tx_hash)
        likecoin_logger.info("ekil send: recipient: "+_recipient)
        likecoin_logger.info("ekil send: amount: "+str(_amount))
        likecoin_logger.info("ekil send: fee: "+str(_fee))

        # database.add_tx_evm_to_like(
        #     to_contract_txid = _txid_evm,
        #     from_vault_txid = tx_hash,
        #     like_address = _recipient
        # )
        response = {"status":"success","tx_id":tx_hash}
        return response

    except Exception as e:
        print(str(e))
        likecoin_logger.error(e)    
        response = {"status":"failure","message":str(e)}
        return response


# def send_check(txid):
#     try:
#         client = pymongo.MongoClient(MONGODB_URL)
#         db = client.finish_tx
#         like = db.like
#         tx_data = ""
#         tx_data = like.find_one({"to_contract_txid":txid})
#         if tx_data == None:
#             response = {"status":"success","message":"this txid has not been sent yet."}
#             return response
#         response = {"status":"failure","message":"this txid has been sent already."}
#         return response

#     except Exception as e:
#         likecoin_logger.error(e)    
#         response = {"status":"failure","message":"transaction not found or network error."}
#         return response

def logging_test():
    likecoin_logger.info("hello world")
    likecoin_logger.warning("hello world")
    likecoin_logger.error("hello world")
    likecoin_logger.critical("hello world")
    likecoin_logger.debug("hello world")
    database.logging_test()