FROM lnbits/lnbits:v1.3.1

COPY initialize_extensions.py /app/initialize_extensions.py
COPY initialize_balances.py /app/initialize_balances.py

COPY init-lnbits.sh /usr/local/bin/init-lnbits.sh
RUN chmod u+x '/usr/local/bin/init-lnbits.sh'

WORKDIR /app/lnbits/extensions
RUN curl -L -o nwcprovider.tar.gz https://github.com/riccardobl/nwcprovider/archive/refs/tags/1.0.0.tar.gz
RUN tar -xf nwcprovider.tar.gz
RUN mv nwcprovider-1.0.0 nwcprovider
RUN rm nwcprovider.tar.gz
WORKDIR /app

# Will start lnbits and setup extensions and initial accounts.
ENTRYPOINT /usr/local/bin/init-lnbits.sh
