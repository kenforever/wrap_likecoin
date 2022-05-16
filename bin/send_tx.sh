#!/bin/bash
send_tx(){
    expect -c "
    set timeout -1
    spawn /home/kenforever/code/anyway_likecoin/bin/liked tx bank send $from $to $amount --node https://fotan-node-1.like.co:443/rpc/ --keyring-backend file --keyring-dir /home/kenforever/code/anyway_likecoin/bin --chain-id likecoin-mainnet-2 --trace --note \"$note\"
    expect \"Enter keyring passphrase:\"
    send \"$password\r\"
    expect \"confirm transaction before signing and broadcasting*\"
    send \"y\r\"
    expect eof
    "
}

from=''
to=''
amount=''
note=''

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

send_tx $from $to $amount $note