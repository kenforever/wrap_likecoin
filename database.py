import pymongo
import os
import json
import logging
import re
import time
import sys

database_logger: logging.Logger = logging.getLogger(name='database')
database_logger.setLevel(logging.INFO)

handler: logging.StreamHandler = logging.StreamHandler()
formatter: logging.Formatter = logging.Formatter('[%(name)s] %(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
database_logger.addHandler(handler)

mongodb_url = 

def add_tx_like_to_evm(to_vault_txid,from_vault_txid,evm_address,like_address):
    try:
        client = pymongo.MongoClient(mongodb_url)
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
        client = pymongo.MongoClient(mongodb_url)
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
