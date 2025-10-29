#!/bin/bash
set -e

echo "Clearing shared certs"
rm -rf /mnt/lnd/*

echo "Clearing old address"
rm -f /mnt/addresses/${TLS_NAME}.txt

echo "Starting LND"
lnd \
	--bitcoin.regtest \
	--bitcoin.node=bitcoind \
	--noseedbackup \
	--maxpendingchannels=10 \
	--rpclisten=0.0.0.0:10009 \
	--lnddir=/mnt/lnd \
	--tlsextradomain=$TLS_NAME \
	--accept-keysend \
	--bitcoind.rpchost=$BITCOIND_HOST:$BITCOIND_PORT \
	--bitcoind.rpccookie=/mnt/cookie/.cookie \
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

PUB_KEY=$(
	lncli \
		--tlscertpath=/mnt/lnd/tls.cert \
		--macaroonpath=/mnt/lnd/data/chain/bitcoin/regtest/admin.macaroon getinfo \
		| jq -r ".identity_pubkey"
)

echo "Recording public key ${PUB_KEY} so ${CHANNEL_PEER_NAME} can make a channel"
echo $PUB_KEY > /mnt/pubkeys/${TLS_NAME}.txt

echo "Waiting for ${CHANNEL_PEER_NAME}'s public key"
until [ -f "/mnt/pubkeys/${CHANNEL_PEER_NAME}.txt" ]; do
	sleep 1s
done

echo "Creating a channel with ${CHANNEL_PEER_NAME} using ${CHANNEL_LIQUIDITY} sats"
PEER_KEY=$(< "/mnt/pubkeys/${CHANNEL_PEER_NAME}.txt")

sleep 5s

if [ "$CONNECT" = "true" ]; then
	until lncli \
		--tlscertpath=/mnt/lnd/tls.cert \
		--macaroonpath=/mnt/lnd/data/chain/bitcoin/regtest/admin.macaroon connect \
		${PEER_KEY}@${CHANNEL_PEER_NAME}:9735
	do
		sleep 1s
	done
fi

until lncli \
	--tlscertpath=/mnt/lnd/tls.cert \
	--macaroonpath=/mnt/lnd/data/chain/bitcoin/regtest/admin.macaroon openchannel \
	--node_key=${PEER_KEY} \
	--local_amt=${CHANNEL_LIQUIDITY}
do
	sleep 1s
done

echo "Notifying bitcoind that a channel has been created"
touch /mnt/channels/${TLS_NAME}

tail -f /mnt/lnd/logs/bitcoin/regtest/lnd.log

