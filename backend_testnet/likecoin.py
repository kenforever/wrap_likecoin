import json
import requests
import logging
import subprocess
import database
import pymongo
from google.cloud import secretmanager

likecoin_logger: logging.Logger = logging.getLogger(name='likecoin')
likecoin_logger.setLevel(logging.DEBUG)

handler: logging.StreamHandler = logging.StreamHandler()
formatter: logging.Formatter = logging.Formatter('[%(name)s] %(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
likecoin_logger.addHandler(handler)

# get secret from secret manager
# mongodb url
MONGODB_URL_ID = "mongodb_url"
project_id = "wrap-like"
client = secretmanager.SecretManagerServiceClient()
parent = f"projects/{project_id}"
MONGODB_URL_LOCATE = f"{parent}/secrets/{MONGODB_URL_ID}/versions/latest"
MONGODB_URL_RESPONSE = client.access_secret_version(request={"name": MONGODB_URL_LOCATE})
MONGODB_URL = MONGODB_URL_RESPONSE.payload.data.decode("UTF-8")

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

    # check if the transaction is success or not
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
def send_like(recipient_address,amount,evm_txid):

    # send likecoin
    raw_data = subprocess.check_output(
        ['/root/wrap_like/backend/testnet/bin/send_tx.sh',
        f'-f {wlike_vault_address}',
        f'-t {recipient_address}', 
        f'-a {amount}nanoekil',
        f'-n {evm_txid}'
        ]).decode('utf-8')
    likecoin_logger.debug(raw_data)
    
    # get transaction data
    tx_raw_data = raw_data.split('gas estimate:')[1]
    tx_data = json.loads(tx_raw_data)
    tx_hash = tx_data["txhash"]
    logs = tx_data["logs"]

    # if logs is empty means transaction failed
    if logs == [] or logs == None :
        response = {"status":"failure","message":"this transaction did not success.","tx_id":tx_hash}
        likecoin_logger.error(response)
        likecoin_logger.error(tx_data)
        return response

    database.add_tx_evm_to_like(
        to_contract_txid = evm_txid,
        from_vault_txid = tx_hash,
        like_address = recipient_address
    )
    likecoin_logger.info("ekil send: txid: "+tx_hash)
    likecoin_logger.info("ekil send: recipient: "+recipient_address)
    likecoin_logger.info("ekil send: amount: "+str(amount))

    response = {"status":"success","tx_id":tx_hash}
    return response


def send_check(txid):
    try:
        client = pymongo.MongoClient(MONGODB_URL)
        db = client.finish_tx
        like = db.like
        tx_data = ""
        tx_data = like.find_one({"to_contract_txid":txid})
        if tx_data == None:
            response = {"status":"success","message":"this txid has not been sent yet."}
            return response
        response = {"status":"failure","message":"this txid has been sent already."}
        return response

    except Exception as e:
        likecoin_logger.error(e)    
        response = {"status":"failure","message":"transaction not found or network error."}
        return response

