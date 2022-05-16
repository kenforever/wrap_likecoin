import json
import requests
import logging
import subprocess
import database
import pymongo


likecoin_logger: logging.Logger = logging.getLogger(name='likecoin')
likecoin_logger.setLevel(logging.DEBUG)

handler: logging.StreamHandler = logging.StreamHandler()
formatter: logging.Formatter = logging.Formatter('[%(name)s] %(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
likecoin_logger.addHandler(handler)

like_main_rpc_url = "https://mainnet-node.like.co/"
wlike_vault_address = 
mongodb_url = 


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
        ['/home/kenforever/code/anyway_likecoin/bin/send_tx.sh',
        f'-f {wlike_vault_address}',
        f'-t {recipient_address}', 
        f'-a {amount}nanolike',
        f'-n {evm_txid}'
        ]).decode('utf-8')
    likecoin_logger.debug(raw_data)
    
    # get transaction data
    tx_raw_data = raw_data.split('confirm transaction before signing and broadcasting [y/N]: y')[1]
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
    likecoin_logger.info("like send: txid: "+tx_hash)
    likecoin_logger.info("like send: recipient: "+recipient_address)
    likecoin_logger.info("like send: amount: "+str(amount))

    response = {"status":"success","tx_id":tx_hash}
    return response


def send_check(txid):
    try:
        client = pymongo.MongoClient(mongodb_url)
        db = client.finish_tx
        like = db.like
        tx_data = ""
        tx_data = like.find_one({"to_contract_txid":txid})
        if tx_data == None:
            response = {"status":"success","message":"this txid has not been sent yet."}
            return response
        response = {"status":"failure","message":"this txid has been sent already."}
        return response

    except:
        response = {"status":"failure","message":"transaction not found or network error."}
        return response

