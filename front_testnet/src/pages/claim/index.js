import { React, useState, useEffect } from "react";
import "./styles.scss";
import { Status_report } from "./tx_status";

const Claim = () => {
  const [txid, set_txid] = useState("");
  const [target, set_target] = useState("");
  const [submit_status, set_submit_status] = useState("");

  const claim_token = () => {
    if (txid === "" || target === "none") {
      alert("txid is empty");
      return;
    }
    set_submit_status(submit_status + 1);
  };

  const handleChange = (e) => {
    set_target(e.target.value);
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
        <h1 className="title">Claim your token</h1>
        <div className="txid_input">
        <select onChange={handleChange}>
          <option value="none">crossing to...</option>
          <option value="evm">EVM</option>
          <option value="likecoin">likecoin</option>
        </select>
        <input
          className="inputbox"
          type="text"
          onInput={(e) => set_txid(e.target.value)}
          placeholder="paste your txid here."
        />
        </div>

        {submit_status && (
          <Status_report
            txid={txid}
            target={target}
            submit_status={submit_status}
          />
        )}
        <button className="submit" onClick={claim_token}>
          submit
        </button>
      </div>
    </div>
  );
};

export default Claim;
