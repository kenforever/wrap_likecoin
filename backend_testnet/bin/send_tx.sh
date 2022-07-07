#!/bin/bash
send_tx(){
    expect -c "
    set timeout -1
    spawn $keyring/bin/liked tx bank send $from $to $amount --node https://node.testnet.like.co:443/rpc/ --keyring-backend file --keyring-dir $keyring/bin/ --chain-id likecoin-public-testnet-5 -y --note $note -o text --trace
    expect \"Enter keyring passphrase:\"
    send \"$password\r\"
    expect \"confirm transaction before signing and broadcasting*\"
    send \"y\r\"
    "
}

from=''
to=''
amount=''
note=''
keyring=$(pwd)

while getopts "f:t:a:n:" opt; do
  case $opt in
    f)
      from=$OPTARG
      ;;
    t)
      to=$OPTARG
      ;;
    a)
      amount=$OPTARG
      ;;
    n)
      note=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

password='abc123123'

echo "from: $from"  
echo "to: $to"
echo "amount: $amount"
echo "note: $note"
echo "pwd: $keyring"

send_tx $from $to $amount $note
