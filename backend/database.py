import pymongo
import os
import json
import logging
import re
import time
import sys
from google.cloud import secretmanager
import logging.handlers
import os

# database_logger: logging.Logger = logging.getLogger(name='database')
# database_logger.setLevel(logging.INFO)

# handler: logging.StreamHandler = logging.StreamHandler()
# formatter: logging.Formatter = logging.Formatter('[%(name)s] %(asctime)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# database_logger.addHandler(handler)

database_logger: logging.Logger = logging.getLogger(name='database')
database_logger.setLevel(logging.DEBUG)
log_dir = "logs/database"
timefilehandler = logging.handlers.TimedRotatingFileHandler(
    log_dir + os.sep +"database",
    when="D",
    interval=1,
    backupCount=20
)
timefilehandler.suffix = "%Y-%m-%d_%H-%M-%S.log"
formatter: logging.Formatter = logging.Formatter('[%(name)s] %(asctime)s - %(levelname)s - %(message)s')
timefilehandler.setFormatter(formatter)
database_logger.addHandler(timefilehandler)

# get secret from secret manager
# mongodb url
MONGODB_URL_ID = "mongodb_url"
project_id = "wrap-like-dev"
client = secretmanager.SecretManagerServiceClient()
parent = f"projects/{project_id}"
MONGODB_URL_LOCATE = f"{parent}/secrets/{MONGODB_URL_ID}/versions/latest"
MONGODB_URL_RESPONSE = client.access_secret_version(request={"name": MONGODB_URL_LOCATE})
MONGODB_URL = MONGODB_URL_RESPONSE.payload.data.decode("UTF-8")
client = pymongo.MongoClient(MONGODB_URL)
db = client.tx

# def add_tx_like_to_evm(to_vault_txid,from_vault_txid,evm_address,like_address):
#     try:
#         client = pymongo.MongoClient(MONGODB_URL)
#         db = client.finish_tx
#         like = db.evm
#         id = like.insert_one({
#             "to_vault_txid":to_vault_txid,
#             "from_vault_txid":from_vault_txid,
#             "evm_address":evm_address,
#             "like_address":like_address,
#             "finish":True})
#         database_logger.info("like: add finish tx. income txid: {}".format(to_vault_txid))
#         return({"status":"success","id":str(id.inserted_id)})
#     except Exception as e:
#         database_logger.error("Error while adding finish tx to like. to vault txid: {} from contract txid: {}".format(to_vault_txid,from_vault_txid))
#         return(str(e))

# def add_tx_evm_to_like(to_contract_txid,from_vault_txid,like_address):
#     try:
#         client = pymongo.MongoClient(MONGODB_URL)
#         db = client.finish_tx
#         evm = db.like
#         id = evm.insert_one({
#             "to_contract_txid":to_contract_txid,
#             "from_vault_txid":from_vault_txid,
#             "like_address":like_address,
#             "finish":True})
#         database_logger.info("evm: add finish tx. income txid: {}".format(to_contract_txid))
#         return({"status":"success","id":str(id.inserted_id)})
#     except Exception as e:
#         database_logger.error("Error while adding finish tx to evm. to contract txid: {} from contract txid: {}".format(to_contract_txid,from_vault_txid))
#         return(str(e))

def logging_test():
    database_logger.info("logging test")
    database_logger.warning("logging test")
    database_logger.error("logging test")
    database_logger.critical("logging test")

def database_test():
    like = db.like
    _like_delete_testuse_query = {"to_vault_txid":"testuse"}
    _like_delete_testuse = like.delete_many(_like_delete_testuse_query)
    print(_like_delete_testuse.deleted_count,"deleted testuse")

    add_tx_like_to_evm("testuse","testuse","testuse")
    update_tx_status_like_to_evm("testuse","testuse","finished")

    #evm
    evm = db.evm
    _evm_delete_testuse_query = {"to_contract_txid":"testuse"}
    _evm_delete_testuse = evm.delete_many(_evm_delete_testuse_query)
    print(_evm_delete_testuse.deleted_count,"deleted testuse")

    add_tx_evm_to_like("testuse","testuse","testuse")
    update_tx_status_evm_to_like("testuse","testuse","finished")


def add_tx_like_to_evm(to_vault_txid,evm_address,like_address):
    try:
        like = db.like
        id = like.insert_one({
            "to_vault_txid":to_vault_txid,
            "evm_address":evm_address,
            "like_address":like_address,
            "status":"tx_submited"})
        database_logger.info("[like] add new tx, to_vault_txid: {}".format(to_vault_txid))
        return({"status":"success","id":str(id.inserted_id)})
    except Exception as e:
        database_logger.error("[like] Error while adding tx into like. to_vault_txid: {}, error:{}".format(to_vault_txid,str(e)))
        return(str(e))


def add_tx_evm_to_like(to_contract_txid:str,from_vault_txid:str,like_address:str,amount:int):
    try:
        evm = db.evm
        id = evm.insert_one({
            "to_contract_txid":to_contract_txid,
            "from_vault_txid":from_vault_txid,
            "like_address":like_address,
            "amount":amount,
            "status":"tx_submited"})
        database_logger.info("[evm] add new tx, to_contract_txid: {}".format(to_contract_txid))
        return({"status":"success","id":str(id.inserted_id)})
    except Exception as e:
        database_logger.error("[evm] Error while adding tx into evm. to_contract_txid: {}, error:{}".format(to_contract_txid,str(e)))
        return(str(e))


def update_tx_status_like_to_evm(to_vault_txid, from_contract_txid, status):
    try:
        like = db.like
        query = { "to_vault_txid": to_vault_txid }
        update_status = { "$set": {"from_contract_txid": from_contract_txid, "status": status} }
 
        update_result = like.update_one(query, update_status)

        database_logger.info("[like] {} tx(s) updated. to_vault_txid: {}, status: {}".format(update_result.modified_count,to_vault_txid,status))

    except Exception as e:
        database_logger.error("[like] Error while adding tx into evm. to_vault_txid: {}, error: {}".format(to_vault_txid,str(e)))
        return(str(e))

def update_tx_status_evm_to_like(to_contract_txid, status):
    try:
        evm = db.evm
        query = { "to_contract_txid": to_contract_txid }
        update_status = { "$set": {"status": status} }
 
        update_result = evm.update_one(query, update_status)

        database_logger.info("[evm] {} tx(s) updated. to_contract_txid: {}, status: {}".format(update_result.modified_count,to_contract_txid,status))

    except Exception as e:
        database_logger.error("[evm] Error while adding tx into evm. to_contract_txid: {}, error: {}".format(to_contract_txid,str(e)))
        return(str(e))

def evm_to_like_transaction_check(txid):
    evm = db.evm
    query = { "to_contract_txid": txid }
    search = []
    search = list(evm.find(query))
    if len(search) == 0:
        response = {"status":"success","message":"txid not mint."}
        return response
    status = search[0]["status"]
    if status == "finish":
        from_vault_txid = search[0]["from_vault_txid"]
        response = {"status":"failure","message":"txid already mint.","txid":from_vault_txid}
        return response
    from_vault_txid = search[0]["from_vault_txid"]
    response = {"status":"failure","message":"tx submited.","txid":from_vault_txid}
    return response
    
    
    