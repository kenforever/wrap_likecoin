import pymongo
import os
import json
from fastapi import FastAPI, HTTPException, Depends, status
import web3
import cross_chain
import likecoin
import wlike


app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/likecoin/cross/to/{target}")
def wlike_mint(target: str, txid: str):
    if target == "evm":
        return cross_chain.likecoin_to_wlike(txid)
    elif target == "likecoin":
        return cross_chain.wlike_to_likecoin(txid)
    else:
        return {"status":"failure","message":"unknown target."}

# @app.get("/likecoin/txid/{txid}")
# def mint_check_all(txid: str):
#     if txid[:2] == "0x":
#         return wlike.transaction_check(txid)
#     return likecoin._check(txid)

@app.get("/likecoin/cross/status/{txid}")
def cross_status(txid: str):
    if txid[:2] == "0x":
        return wlike.mint_check(txid)
    return likecoin.transaction_check(txid)


