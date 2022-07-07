import pymongo
import os
import json
import logging
import re
import time
import sys
from google.cloud import secretmanager

database_logger: logging.Logger = logging.getLogger(name='database')
database_logger.setLevel(logging.INFO)

handler: logging.StreamHandler = logging.StreamHandler()
formatter: logging.Formatter = logging.Formatter('[%(name)s] %(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
database_logger.addHandler(handler)

# get secret from secret manager
# mongodb url
MONGODB_URL_ID = "mongodb_url"
project_id = "wrap-like"
client = secretmanager.SecretManagerServiceClient()
parent = f"projects/{project_id}"
MONGODB_URL_LOCATE = f"{parent}/secrets/{MONGODB_URL_ID}/versions/latest"
MONGODB_URL_RESPONSE = client.access_secret_version(request={"name": MONGODB_URL_LOCATE})
MONGODB_URL = MONGODB_URL_RESPONSE.payload.data.decode("UTF-8")


def add_tx_like_to_evm(to_vault_txid,from_vault_txid,evm_address,like_address):
    try:
        client = pymongo.MongoClient(MONGODB_URL)
        db = client.finish_tx
        like = db.evm
        id = like.insert_one({
            "to_vault_txid":to_vault_txid,
            "from_vault_txid":from_vault_txid,
            "evm_address":evm_address,
            "like_address":like_address,
            "finish":True})
        database_logger.info("like: add finish tx. income txid: {}".format(to_vault_txid))
        return({"status":"success","id":str(id.inserted_id)})
    except Exception as e:
        database_logger.error("Error while adding finish tx to like. to vault txid: {} from contract txid: {}".format(to_vault_txid,from_vault_txid))
        return(str(e))

def add_tx_evm_to_like(to_contract_txid,from_vault_txid,like_address):
    try:
        client = pymongo.MongoClient(MONGODB_URL)
        db = client.finish_tx
        evm = db.like
        id = evm.insert_one({
            "to_contract_txid":to_contract_txid,
            "from_vault_txid":from_vault_txid,
            "like_address":like_address,
            "finish":True})
        database_logger.info("evm: add finish tx. income txid: {}".format(to_contract_txid))
        return({"status":"success","id":str(id.inserted_id)})
    except Exception as e:
        database_logger.error("Error while adding finish tx to evm. to contract txid: {} from contract txid: {}".format(to_contract_txid,from_vault_txid))
        return(str(e))
