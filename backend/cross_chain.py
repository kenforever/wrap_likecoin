import wlike
import likecoin 
import logging
import logging.handlers
import os
import database

token_decimals = 18

logging.basicConfig(level=logging.DEBUG)
bridge_logger: logging.Logger = logging.getLogger(name='bridge')
bridge_logger.setLevel(logging.DEBUG)
log_dir = "logs/bridge"
timefilehandler = logging.handlers.TimedRotatingFileHandler(
    log_dir + os.sep +"bridge",
    when="D",
    interval=1,
    backupCount=20
)
timefilehandler.suffix = "%Y-%m-%d_%H-%M-%S.log"
formatter: logging.Formatter = logging.Formatter('[%(name)s] %(asctime)s - %(levelname)s - %(message)s')
timefilehandler.setFormatter(formatter)
bridge_logger.addHandler(timefilehandler)

# file_handler = logging.FileHandler("./logs/bridge.log")
# file_handler.setLevel(logging.DEBUG)
# logger.addHandler(file_handler)

# send like to evm
# if success, return should look like this:
# {
#     "status":"success",
#     "txid":{txid}
# }
def likecoin_to_wlike(like_txid):
    try:
        # check if the transaction have any problem
        # and get the recipient address and amount of likecoin going to send
        likecoin_tx = likecoin.transaction_check(like_txid)
        if likecoin_tx["status"] != "success":
            return likecoin_tx
        
        recipient_evm = likecoin_tx["recipient"]

        # amount here should be 1:1 on likecoin
        amount = likecoin_tx["amount"]
        # exchange likecoin to wlike 
        # because counting mathod is different on evm and likecoin chain
        # we need to convert the amount to evm
        # the token_decimals is set to 18
        # the formula is:
        amount = amount * (10 ** token_decimals)

        # the recipient address in likecoin tx memo should match the address that are going to send to
        # if recipient_evm != evm_address:
        #     bridge_logger.info("recipient address mismatch. evm: {}, recever: {}".format(evm_address,recipient_evm))
        #     return {"status":"failure","message":"recipient address mismatch."}

        # check if this txid has been mint or not
        mint_check = wlike.mint_check(like_txid)
        if mint_check["status"] == "failure":
            return mint_check

        if mint_check["status"] == "true":
            bridge_logger.info("this txid has been mint. txid: {}".format(like_txid))
            response = {"status":"failure","message":"this txid has been mint."}
            return response

        amount = int(amount)
        response = wlike.mint_wlike(recipient_evm,amount,like_txid)
        if response["status"] != "success":
            bridge_logger.error("evm mint error. txid: {}".format(like_txid))
            bridge_logger.error("evm mint error. tx info: {}".format(response))
            return response
        return response

    except Exception as e:
        bridge_logger.error("bridge error: likecoin to evm.")
        bridge_logger.error("error message:" + str(e))
        return {"status":"failure","message":"unknown error."}

def wlike_to_likecoin(evm_txid):
    try:
        evm_tx = wlike.transaction_check(evm_txid)
        if evm_tx["status"] != "success":
            print(evm_tx)
            return evm_tx
        bridge_logger.debug("evm txid: checked")

        # check this txid is sent or not
        send_check = database.evm_to_like_transaction_check(evm_txid)
        if send_check["status"] == "failure":
            return send_check
        bridge_logger.debug("send check: checked")

        like_recipient_address = evm_tx["recipient"]
        amount = evm_tx["amount"]
        # like to nanolike
        # 1 like = 1000000000 nanolike
        # formula beloew:
        # the number after point will not be send.
        amount = float(amount) * 1000000000
        amount = int(amount)
        
        # if like_recipient_address != like_address:
        #     return {"status":"failure","message":"recipient address mismatch."}

        tx = likecoin.send_like(like_recipient_address,amount,evm_txid)
        if tx['status'] != 'success':
            bridge_logger.error("likecoin send error. txid: {}".format(evm_txid))
            bridge_logger.error("likecoin send error. tx info: {}".format(tx))
            return tx
        bridge_logger.info("likecoin send success. txid: {}".format(tx["tx_id"]))
        return {"status":"success","txid":tx["tx_id"]}
    except Exception as e:
        bridge_logger.error("bridge error: evm to likecoin.")
        bridge_logger.error("error message:" + str(e))
        return {"status":"failure","message":"unknown error."}


def logging_test():
    bridge_logger.debug("debug message")
    bridge_logger.info("info message")
    bridge_logger.warning("warning message")
    bridge_logger.error("error message")
    bridge_logger.critical("critical message")