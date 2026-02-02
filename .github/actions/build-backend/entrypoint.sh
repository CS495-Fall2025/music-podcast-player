#!/bin/sh -l

set -e

ls /github/workspace

cp /github/workspace/backend/requirements.txt /app/
cp /github/workspace/backend/pyproject.toml /app/src/

# Install backend dependencies
pip3 install -r /app/requirements.txt -t /app/

# Install backend package
cp -r /github/workspace/backend/src/rss_music_backend /app/src/rss_music_backend
pip3 install /app/src -t /app/

cp /github/workspace/backend/lambda_handler.py /app/

# Package dynamic libraries used by some packages.
cp /github/workspace/backend/copy_lib_requirements.py /app/
mkdir lib
python3 copy_lib_requirements.py

# Remove unneeded files
rm -rf /app/src
rm -rf /app/bin
find /app -name "__pycache__" -type d -exec rm -rf {} +
rm copy_lib_requirements.py

zip /github/workspace/build/backend-build.zip -r .
