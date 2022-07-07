import abi from "./abi.json";
import React, { useEffect, useState } from "react";
import { ethers } from "ethers";

const From_metamask = (props) => {

    async function testing(){
        const provider = new ethers.providers.Web3Provider(window.ethereum,"any");
        const { chainId } = await provider.getNetwork()
        console.log(chainId) // 42
        
        if (chainId !== 4) {
            alert("Please switch to the rinkeby testnet");
            return;
        }
        
        const signer = provider.getSigner()
        
        let wlike_address = "0x5A9Ed15Bb303bca3F814710466eb53B31e5AA48c";

        let wlike_Contract = new ethers.Contract(wlike_address, abi, provider);

        // let wlike_contract = new window.ethereum.Contract(abi, wlike_address);
        // // var Contract = require('web3-eth-contract');

        const test = await wlike_Contract.burnable();
        const wlike_with_signer = wlike_Contract.connect(signer);
        const amount = ethers.utils.parseUnits("10.0", 18);
        // let testing = wlike_contract.methods.burnable().call().then(console.log);
        console.log("burnable"+test);
        const test_address = "like1teqq9gt4sczfyng3rly5cds4tfew28gauuxp3z";
        const wlike_tx = wlike_with_signer.cross(amount, test_address);
        console.log(wlike_tx)


};
return (
    <div>
        <h1>from_metamask</h1>
        {/* <p>wlike_address: {wlike_address}</p>
        <p>wlike_contract: {wlike_Contract}</p> */}
        {/* <p>testing: {testing}</p> */}
        <button className="Change_burnable"
        onClick={() => testing()}
        >
            cross 
        </button>
    </div>
);

};
export default From_metamask;
