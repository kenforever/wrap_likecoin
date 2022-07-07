import React, { useEffect, useState } from "react";

async function connect(onConnected) {
  if (!window.ethereum) {
    alert("Get MetaMask!");
    return;
  }

  const accounts = await window.ethereum.request({
    method: "eth_requestAccounts",
  });

  onConnected(accounts[0]);
}

async function check_connection(onConnected) {
  if (window.ethereum) {
    const accounts = await window.ethereum.request({
      method: "eth_accounts",
    });

    if (accounts.length > 0) {
      const account = accounts[0];
      onConnected(account);
      return;
    }
  }
}

function isMobileDevice() {
  return "ontouchstart" in window || "onmsgesturechange" in window;
}

function Connect({ setUserAddress }) {
  if (isMobileDevice()) {
    const dappUrl = "metamask-auth.ilamanov.repl.co"; // TODO enter your dapp URL. For example: https://uniswap.exchange. (don't enter the "https://")
    const metamaskAppDeepLink = "https://metamask.app.link/dapp/" + dappUrl;
    return (
      <a href={metamaskAppDeepLink}>
        <button className={styles.button}>Connect to MetaMask</button>
      </a>
    );
  }
  function Address({ userAddress }) {
    return (
      <span className={styles.address}>
        {userAddress.substring(0, 5)}…
        {userAddress.substring(userAddress.length - 4)}
      </span>
    );
  }
}

const Metamask_connect = () => {
  const [address, set_address] = useState("");

  useEffect(() => {
    check_connection(set_address);
  }, []);
  useEffect(() => {
    onAddressChange(address);
  }, [address]);
  return userAddress ? (
    <div>
      Connected with <Address userAddress={userAddress} />
    </div>
  ) : (
    <Connect setUserAddress={setUserAddress} />
  );
};

export default Metamask_connect;
