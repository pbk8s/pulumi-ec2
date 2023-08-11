#!/bin/bash

if [ ! -f pp.f ] 
then
  echo -n "Enter your passphrase: "
  read -s pphrase
  echo $pphrase > pp.f
fi

export PULUMI_CONFIG_PASSPHRASE_FILE=pp.f

if [ -f p1-key.pem ] 
then
  echo "You have an private key in p1-key.pem, removing"
  rm -f p1-key.pem
fi

pulumi stack output private_key_pem --show-secrets > p1-key.pem
chmod 400 p1-key.pem

echo "You can SSH now: ssh -i p1-key-pem ubuntu@"
