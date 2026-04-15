FROM bitcoin/bitcoin:latest

COPY init-bitcoind.sh /usr/local/bin/init-bitcoind.sh
RUN chmod u+x '/usr/local/bin/init-bitcoind.sh'

# Will start bitcoind and setup the miner wallet.
ENTRYPOINT /usr/local/bin/init-bitcoind.sh
