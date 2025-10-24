#!/bin/bash
set -e

echo "Clearing shared certs"
rm -rf /mnt/lnd/*

echo "Waiting for bitcoind"
until curl -s --user $RPC_USER:$RPC_PASS http://$BITCOIND_HOST:$BITCOIND_PORT/ \
		-d '{"jsonrpc":"1.0","id":"curltest","method":"getblockchaininfo","params":[]}' \
		| grep -q '"result"'; do
	sleep 1
	curl --user $RPC_USER:$RPC_PASS http://$BITCOIND_HOST:$BITCOIND_PORT/ \
		-d '{"jsonrpc":"1.0","id":"curltest","method":"getblockchaininfo","params":[]}'
done

echo "Starting LND"
lnd \
	--bitcoin.regtest \
	--bitcoin.node=bitcoind \
	--noseedbackup \
	--maxpendingchannels=10 \
	--rpclisten=0.0.0.0:10009 \
	--lnddir=/mnt/lnd \
	--tlsextradomain=$TLS_NAME \
	--bitcoind.rpchost=$BITCOIND_HOST:$BITCOIND_PORT \
	--bitcoind.rpcuser=$RPC_USER \
	--bitcoind.rpcpass=$RPC_PASS \
	--bitcoind.zmqpubrawblock=tcp://$BITCOIND_HOST:28332 \
	--bitcoind.zmqpubrawtx=tcp://$BITCOIND_HOST:28333 &

echo "Waiting for LND to be ready"
until lncli \
	--tlscertpath=/mnt/lnd/tls.cert \
	--macaroonpath=/mnt/lnd/data/chain/bitcoin/regtest/admin.macaroon getinfo \
	> /dev/null 2>&1
do
	sleep 1s
done

WALLET_ADDR=$(
	lncli \
		--tlscertpath=/mnt/lnd/tls.cert \
		--macaroonpath=/mnt/lnd/data/chain/bitcoin/regtest/admin.macaroon newaddress p2wkh \
		| jq -r ".address"
)

echo "Recording wallet address ${WALLET_ADDR} so it can be funded"
echo $WALLET_ADDR > /mnt/addresses/${TLS_NAME}.txt

tail -f /mnt/lnd/logs/bitcoin/regtest/lnd.log

