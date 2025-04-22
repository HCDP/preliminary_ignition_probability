#!/bin/bash

echo "[task.sh] [1/?] Starting Execution."
export TZ="HST"
echo "It is currently $(date)."
if [ $CUSTOM_DATE ]; then
    echo "An aggregation date was provided by the environment."
else
    export CUSTOM_DATE=$(date -d "1 day ago" --iso-8601)
    echo "No aggregation date was provided by the environment. Defaulting to yesterday."
fi
echo "Aggregation date is: " $CUSTOM_DATE
#RENAME .ENV AS NEEDED
source /workspace/envs/pred_dev.env

echo "[task.sh] [2/?] Fetching dependencies, all counties."
python3 -W ignore /workspace/code/wget_dependencies.py $CUSTOM_DATE

echo "[task.sh] [3/?] Running map workflow, all counties"
python3 -W ignore /workspace/code/generate_ignition_forecast.py bi $CUSTOM_DATE
python3 -W ignore /workspace/code/generate_ignition_forecast.py ka $CUSTOM_DATE
python3 -W ignore /workspace/code/generate_ignition_forecast.py mn $CUSTOM_DATE
python3 -W ignore /workspace/code/generate_ignition_forecast.py oa $CUSTOM_DATE

echo "[task.sh] [4/?] Creating statewide mosaic."
python3 -W ignore /workspace/code/statewide_mosaic.py

echo "[task.sh] [5/?] Preparing upload config."
cd /sync
python3 inject_upload_config.py config.json $CUSTOM_DATE

echo "[task.sh] [6/?] Uploading data."
python3 upload.py

echo "[task.sh] All done!"