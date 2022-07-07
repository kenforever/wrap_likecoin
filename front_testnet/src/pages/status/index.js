import { React, useState } from "react";
import "./styles.scss";
import { Status_report } from "./tx_status";

const Claim = () => {
  const [txid, set_txid] = useState("");
  const [show_status, set_show_status] = useState(false);
  const [submit_txid, set_submit_txid] = useState("");
  console.log(show_status)
  // const claim_token = () => {
  //   let url = "http://127.0.0.1:8000/likecoin/cross/to/" + target_chain;
  //   fetch(url)
  //     .then((res) => res.json())
  //     .then((data) => {
  //       console.log(data);
  //       if (data.status == "success") {
  //         setstatus("success");
  //       }
  //     });
  // };
  const claim_token = () => {
    console.log("outside: "+txid);
    set_show_status(true);
    set_submit_txid(txid);
  };

  return (
    <div
      className="container"
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "90vh",
      }}
    >
      <div className="Panel">
        <h1 className="title">Check the mint/transaction progress</h1>
        <input
          className="inputbox"
          type="text"
          onInput={(e) => set_txid(e.target.value)}
          placeholder="paste your txid here."
        />
        
        {show_status && <Status_report txid={submit_txid}/>}
        <button className="submit" onClick={claim_token}>
          submit
        </button>
      </div>
    </div>
  );
};

export default Claim;
