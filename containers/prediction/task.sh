#!/bin/bash

echo "[task.sh] [1/6] Starting Execution."
export TZ="HST"
echo "It is currently $(date)."
if [ $CUSTOM_DATE ]; then
    echo "An aggregation date was provided by the environment."
else
    export CUSTOM_DATE=$(date -d "1 day ago" --iso-8601)
    echo "No aggregation date was provided by the environment. Defaulting to yesterday."
fi
echo "Aggregation date is: " $CUSTOM_DATE
source /workspace/envs/prod.env

echo "[task.sh] [2/6] Fetching dependencies, all counties."
python3 -W ignore /workspace/code/prediction/wget_dependencies.py $CUSTOM_DATE

echo "[task.sh] [3/6] Running map workflow, all counties"
python3 -W ignore /workspace/code/prediction/generate_ignition_forecast.py bi $CUSTOM_DATE
python3 -W ignore /workspace/code/prediction/generate_ignition_forecast.py ka $CUSTOM_DATE
python3 -W ignore /workspace/code/prediction/generate_ignition_forecast.py mn $CUSTOM_DATE
python3 -W ignore /workspace/code/prediction/generate_ignition_forecast.py oa $CUSTOM_DATE

echo "[task.sh] [4/6] Creating statewide mosaic."
python3 -W ignore /workspace/code/prediction/statewide_mosaic.py

echo "[task.sh] [5/6] Preparing upload config."
cd /sync
python3 inject_upload_config.py config.json $CUSTOM_DATE

echo "[task.sh] [6/6] Uploading data."
python3 upload.py

echo "[task.sh] All done!"