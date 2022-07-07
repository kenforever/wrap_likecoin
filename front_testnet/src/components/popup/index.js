import React from "react";
import "./index.scss";
import { ethers } from "ethers";
import { StdFee } from "@cosmjs/launchpad";
import { SigningStargateClient } from "@cosmjs/stargate";
import { Registry, OfflineSigner, EncodeObject, DirectSecp256k1HdWallet } from "@cosmjs/proto-signing";
import { SigningCosmosClient } from "@cosmjs/launchpad";
const Popup = (props) => {
  async function metamask_connect() {
    const provider = new ethers.providers.Web3Provider(window.ethereum,"any");
      const accounts = await window.ethereum.request({
        method: "eth_requestAccounts",
        });
        const signer = provider.getSigner()
        console.log("ac: ", await signer.getAddress());
        if (accounts.length > 0) {
            const signer = provider.getSigner()
            props.set_address(accounts);
            return;
        }
      window.ethereum.request({
          method: "wallet_addEthereumChain",
          params: [{
              chainId: "0x89",
              rpcUrls: ["https://rpc-mainnet.matic.network/"],
              chainName: "Matic Mainnet",
              nativeCurrency: {
                  name: "MATIC",
                  symbol: "MATIC",
                  decimals: 18
              },
              blockExplorerUrls: ["https://polygonscan.com/"]
          }]
      });
    }

    async function keplr_connect() {
        if (!window.keplr){
            alert("Get keplr!");
            return;
        }

        const chainId = "likecoin-public-testnet-5";
        await window.keplr.enable(chainId);
        const offlineSigner = window.keplr.getOfflineSigner(chainId);
        const accounts = await offlineSigner.getAccounts();
        const cosmJS = new SigningCosmosClient(
            "https://lcd-cosmoshub.keplr.app",
            accounts[0].address,
            offlineSigner,
        );
        console.log("ac: ", accounts[0].address);
    
    }
  return props.trigger ? (
    <>
      <div className="popup">
        <div className="popup_inner">
          <h1>hi!</h1>
          <p>try connect wallet?</p>
          <button
            className="close_button"
            onClick={() => props.set_trigger(false)}
          >
            Close
          </button>
          <button
            className="metamask_connect"
            onClick={() => metamask_connect()}
          >
            metamask
          </button>
          <button
            className="keplr_connect"
            onClick={() => keplr_connect()}
          >
            keplr
          </button>
        </div>
      </div>
    </>
  ) : null;
};

export default Popup;
