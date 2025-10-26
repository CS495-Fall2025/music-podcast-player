#!/bin/bash

set -e

source /app/.venv/bin/activate
echo "Setting up extensions"
python /app/initialize_extensions.py
deactivate

echo "Running LNBits"
uv run lnbits --port $LNBITS_PORT --host $LNBITS_HOST --forwarded-allow-ips='*' \
	> /var/log/lnbits.log 2>&1 &

echo "Waiting for LNBits to be ready"
until curl -s -X GET http://localhost:5000/api/v1/health; do
	sleep 1s
done

sleep 10s
source /app/.venv/bin/activate
echo "Setting up initial account and funds"
python /app/initialize_balances.py
deactivate

tail -f /var/log/lnbits.log


