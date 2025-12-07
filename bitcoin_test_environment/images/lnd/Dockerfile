FROM lightninglabs/lnd:v0.19.3-beta

COPY init-lnd.sh /usr/local/bin/init-lnd.sh
RUN chmod u+x '/usr/local/bin/init-lnd.sh'

# Will start lnd and setup the listener and artist wallets.
ENTRYPOINT /usr/local/bin/init-lnd.sh
