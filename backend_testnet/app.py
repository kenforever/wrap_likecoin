from pydantic import BaseModel
import pymongo
import os
import json
from fastapi import FastAPI, HTTPException, Depends, status
import web3
import cross_chain
import likecoin
import wlike
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum

app = FastAPI()

PREFIX = "/testnet"

origins = [
        "http://localhost:80",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class cross_txid(BaseModel):
    txid: str

class target(str, Enum):
    likecoin = 'likecoin'
    evm = "evm"

@app.get(PREFIX+"/")
def root():
    return {"message": "Hello World"}

@app.post(PREFIX+"/likecoin/cross/to/{target}")
def wlike_mint(target: target, txid: cross_txid):
    txid = txid.dict()["txid"]
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


# this api is checking for is the txid has been mint or not
# or is the txid has been sent or not
# if get any return, it means the txid has been sent or mint
# if not, it means the txid has not been sent or mint 
# or the txid is not exist
@app.get(PREFIX+"/likecoin/cross/status/{txid}")
def cross_status(txid: str):
    if txid[:2] == "0x":
        return wlike.mint_check(txid)
    return likecoin.transaction_check(txid)


