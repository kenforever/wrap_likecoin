import { React, useState, useEffect } from "react";
import "./index.scss";

export const Status_report = ( props ) => {
  console.log(props)
  console.log("report " + props.txid);
  const [tx_status, set_tx_status] = useState("");
  const [success_txid_report, set_success_txid_report] = useState({
    txid: "",
  });
  const [fail_txid_report, set_fail_txid_report] = useState({
    reason: "",
  });

  useEffect(() => {
    console.log("effect using: "+props.txid)
    let url = "https://api.anyway.network/testnet/likecoin/cross/to/" + props.target;
    fetch(url,{
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        txid: props.txid,
      }),
    })

      .then((res) => res.json())
      .then((data) => { 
        console.log(data);
        if (data.status === "success") {
          set_tx_status(data.status);
          set_success_txid_report({
            recipient: data.txid,
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
  }, [props.txid]);
  return (
    <div className="tx_report">
      {tx_status === "success" ? (
        <div>
          <h1>status</h1><p>{tx_status}</p>
          <p>{props.txid}</p>
          <p>{success_txid_report.txid}</p>
        </div>
      ) : (
        <div>
          <h1>status</h1><p>{tx_status}</p>
          <p>{props.txid}</p>
          <p>{fail_txid_report.reason}</p>
        </div>
      )}
    </div>
  );
};
