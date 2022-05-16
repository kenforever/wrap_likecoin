pragma solidity ^0.8.13;
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "hardhat/console.sol";

contract wlike is ERC20,ERC20Burnable {

    address public minter;
    event cross_log(string name, string message);
    mapping(string => bool) public mint_status;

    // address constant burner = 0x0000000000000000000000000000000000000000;

    bool public burnable = false;
    bool public mintable = false;

    constructor(string memory name, string memory symbol) ERC20(name, symbol) {
        // Mint 100 tokens to msg.sender
        // Similar to how
        // 1 dollar = 100 cents
        // 1 token = 1 * (10 ** decimals)
        minter = msg.sender;
    }

    function mint(uint _amount, address receiver, string memory _txid) public {
        console.log(_amount,receiver,_txid);
        require(msg.sender == minter, "you are not allowed to mint new token.");
        require(mintable != false,"mint is temporary disable.");
        require(_amount >0, "amount can not less than zero.");
        bytes memory _txid_bytes = bytes(_txid);
        require(_txid_bytes.length != 0,"txid can not be empty.");
        require(mint_status[_txid] == false, "this txid has been mint.");
        // uint amount;
        // amount = _amount*10**uint(decimals());
        _mint(receiver,_amount);
        mint_status[_txid] = true;
    }

    function cross(uint _amount, string memory _like_address) public{
        require(_amount>0,"burn amount can not less than zero.");
        require(_amount<balanceOf(msg.sender),"amount should be less than your amount.");
        require(burnable != false, "burn function is temporary disable.");
        bytes memory _like_address_bytes = bytes(_like_address);
        require(_like_address_bytes.length != 0,"like address can not be empty.");
        // uint amount;
        // amount = _amount*10**uint(decimals());
        _burn(_msgSender(),_amount);
        emit cross_log("data",_like_address);
    }


    function burnable_switch(bool _status) public{
        require(msg.sender == minter,"your are not allowed to change this switch.");
        require(_status != burnable,"current status is not change.");
        burnable = _status;
    }

    function mintable_switch(bool _status) public {
        require(msg.sender == minter,"your are not allowed to change this switch.");
        require(_status != mintable,"current status is not change.");
        mintable = _status;
    }

    function minter_change(address _target) public{
        require(msg.sender == minter,"your are not allowed to change this switch.");
        require(msg.sender != _target,"this address are already minter.");
        minter = _target;
    }

}
