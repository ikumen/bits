#!/bib/bash

EMULATOR_HOST=localhost
EMULATOR_PORT=8087

export PYTHONPATH=$PYTHONPATH:.
export DATASTORE_EMULATOR_HOST="$EMULATOR_HOST:$EMULATOR_PORT"

#python backend/server.py
python main.py

# dev_appserver.py \
#     --support_datastore_emulator=true \
#     --datastore_emulator_port=$EMULATOR_PORT \
#     --enable_console=yes \
#     --port=8080 \
#     --host=localhost \
#     --dev_appserver_log_level=debug \
#     --storage_path=./tmp \
#     -A "gnoht-bits" \
#     --automatic_restart=false \
#     app.yaml
