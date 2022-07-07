import { React, useState, useEffect } from "react";
import "./index.scss";

export const Status_report = ( txid) => {
  txid = txid.txid;
  console.log("report " + txid);
  const [tx_status, set_tx_status] = useState("");
  const [success_txid_report, set_success_txid_report] = useState({
    recipient: "",
    amount: "",
  });
  const [fail_txid_report, set_fail_txid_report] = useState({
    reason: "",
  });
  useEffect(() => {
    let url = "https://api.anyway.network/testnet/likecoin/cross/status/" + txid;
    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        if (data.status === "success") {
          set_tx_status(data.status);
          set_success_txid_report({
            recipient: data.recipient,
            amount: data.amount,
          });
        } else {
          set_tx_status(data.status);
          set_fail_txid_report({
            reason: data.message,
          });
        }
      })
      .catch((err) => {
        console.log(err);
      });
  }, [txid]);
  return (
    <div className="tx_report">
      {tx_status === "success" ? (
        <div>
          <h1>status</h1><p>{tx_status}</p>
          <p>{success_txid_report.recipient}</p>
          <p>{success_txid_report.amount}</p>
        </div>
      ) : (
        <div>
          <h1>status</h1><p>{tx_status}</p>
          <p>{fail_txid_report.reason}</p>
        </div>
      )}
    </div>
  );
};
