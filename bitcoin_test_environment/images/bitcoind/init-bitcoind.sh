#!/bin/sh

set -e

DATADIR="/home/bitcoin/.bitcoin"

echo "Clearing addresses volume"
rm -rf /mnt/addresses/*

echo "Starting bitcoind..."
bitcoind \
	-regtest=1 \
	-server=1 \
	-rpcbind=0.0.0.0 \
	-rpcport=18443 \
	-rpcallowip=172.0.0.1 \
	-rpcallowip=172.22.0.0/16 \
	-rpcauth=${RPCAUTH} \
	-fallbackfee=0.0002 \
	-daemon \
	-zmqpubrawblock=tcp://0.0.0.0:28332 \
	-zmqpubrawtx=tcp://0.0.0.0:28333

# Wait for RPC to be ready
echo "Waiting for bitcoind RPC..."
until bitcoin-cli -regtest -rpcuser=${RPCUSER} -rpcpassword=${RPCPASSWORD} getblockchaininfo > /dev/null 2>&1; do
	sleep 1s
done

echo "Creating wallet 'miner'..."
bitcoin-cli -regtest -rpcuser=${RPCUSER} -rpcpassword=${RPCPASSWORD} createwallet "miner"
echo "Funding wallet 'miner'..."
miner_address=$(bitcoin-cli -regtest -rpcuser=${RPCUSER} -rpcpassword=${RPCPASSWORD} -rpcwallet=miner getnewaddress)
bitcoin-cli -regtest -rpcuser=${RPCUSER} -rpcpassword=${RPCPASSWORD} generatetoaddress 200 ${miner_address}

OLD_IFS=$IFS
IFS=","
set -- $FUNDED_NODES
IFS=$OLD_IFS

echo "Waiting for LND wallet addresses from funded nodes"
for NODE in "$@"; do
	while [ ! -s "/mnt/addresses/${NODE}.txt" ]; do
		sleep 1
	done
done

echo "Funding nodes"
for NODE in "$@"; do
	address=$(cat "/mnt/addresses/${NODE}.txt")
	echo "Funding ${address} with 1.0 BTC"
	bitcoin-cli -regtest -rpcuser=${RPCUSER} -rpcpassword=${RPCPASSWORD} sendtoaddress "${address}" 1.0
done

echo "Mining to confirm"
bitcoin-cli -regtest -rpcuser=${RPCUSER} -rpcpassword=${RPCPASSWORD} generatetoaddress 6 ${miner_address}


# Keep the container alive and print logs
tail -f ~/.bitcoin/regtest/debug.log

