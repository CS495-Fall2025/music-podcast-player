# Developing the backend

The backend for our music player uses [Flask](https://flask.palletsprojects.com/en/stable/).
It should consist of a stateless REST API (state should be handled by the database).

## Setup Development Environment

In order to work on the backend, you will need to make a virtual environment, which will
locally provide the dependencies for running it.

```bash
# Create the venv
python -m venv dev_venv
```

```
# Activate the venv

# Windows (command)
dev_venv\Scripts\activate.bat

# Windows (Powershell, make sure to enable running scripts)
dev_venv\Scripts\Activate.ps1

# MacOS/Linux
source dev_venv/bin/activate
```

```bash
# Install dependancies in venv
pip install -r dev-requirements.txt
```

```bash
# When you are done with the environment, you can deactivate it like so
deactivate
```

## Run the backend (debug mode)

```bash
python3 run_debug.py
```

## Send requests to the backend (examples using Curl)

```bash
curl -X GET http://localhost:5000/endpoint
curl -X POST -H "Content-Type: application/json" -d '{"json": "data"}' http://localhost:5000/endpoint
```

## Run linting, formatting, testing

```bash
# Linting
python -m ruff check

# Formatting Check
python -m ruff format --check

# Formatting Fix
python -m ruff format

# Run Tests
python -m pytest
```
