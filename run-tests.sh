#!/bib/bash

EMULATOR_HOST=localhost
EMULATOR_PORT=8087

export PYTHONPATH=$PYTHONPATH:.
export DATASTORE_EMULATOR_HOST="$EMULATOR_HOST:$EMULATOR_PORT"

#python backend/server.py
pytest -s tests/ --disable-pytest-warnings
