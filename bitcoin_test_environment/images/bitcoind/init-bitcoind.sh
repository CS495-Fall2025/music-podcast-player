#!/bin/sh

set -e

DATADIR="/home/bitcoin/.bitcoin"

echo "Clearing cookie volume"
rm -rf /mnt/cookie/*

echo "Starting bitcoind..."
bitcoind \
	-regtest=1 \
	-server=1 \
	-rpcbind=0.0.0.0 \
	-rpcport=18443 \
	-rpcallowip=0.0.0.0/0 \
	-rpccookiefile=/mnt/cookie/.cookie \
	-fallbackfee=0.0002 \
	-daemon \
	-zmqpubrawblock=tcp://0.0.0.0:28332 \
	-zmqpubrawtx=tcp://0.0.0.0:28333

# Wait for RPC to be ready
echo "Waiting for bitcoind RPC..."
until bitcoin-cli -regtest -rpccookiefile=/mnt/cookie/.cookie getblockchaininfo > /dev/null 2>&1; do
	sleep 1s
done

echo "Creating wallet 'miner'..."
bitcoin-cli -regtest -rpccookiefile=/mnt/cookie/.cookie createwallet "miner"
echo "Funding wallet 'miner'..."
miner_address=$(bitcoin-cli -regtest -rpccookiefile=/mnt/cookie/.cookie -rpcwallet=miner getnewaddress)
bitcoin-cli -regtest -rpccookiefile=/mnt/cookie/.cookie generatetoaddress 200 ${miner_address}

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
	bitcoin-cli -regtest -rpccookiefile=/mnt/cookie/.cookie sendtoaddress "${address}" 1.0
done

echo "Mining to confirm"
bitcoin-cli -regtest -rpccookiefile=/mnt/cookie/.cookie generatetoaddress 6 ${miner_address}

echo "Waiting for LND channels"
for NODE in "$@"; do
	until [ -f "/mnt/channels/${NODE}" ]; do
		sleep 1
	done
done

echo "Mining to confirm channels"
bitcoin-cli -regtest -rpccookiefile=/mnt/cookie/.cookie generatetoaddress 6 ${miner_address}

# Keep the container alive and print logs
tail -f ~/.bitcoin/regtest/debug.log

