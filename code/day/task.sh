#!/bin/bash

set -euo pipefail

echo "[task.sh] [1/5] Starting Execution."
export TZ="HST"
echo "It is currently $(date)."
if [[ -v CUSTOM_DATE ]]; then
    echo "An aggregation date was provided by the environment."
else
    export CUSTOM_DATE=$(date -d "1 day ago" --iso-8601)
    echo "No aggregation date was provided by the environment. Defaulting to yesterday."
fi
echo "Aggregation date is: " $CUSTOM_DATE

echo "[task.sh] [2/5] Fetching dependencies, all counties."
python3 -W ignore /home/hawaii_climate_products_container/preliminary/ignition_prob/code/day/wget_dependencies.py $CUSTOM_DATE

echo "[task.sh] [3/5] Generating API, all counties."
python3 -W ignore /home/hawaii_climate_products_container/preliminary/ignition_prob/code/day/generate_api.py bi $CUSTOM_DATE
python3 -W ignore /home/hawaii_climate_products_container/preliminary/ignition_prob/code/day/generate_api.py ka $CUSTOM_DATE
python3 -W ignore /home/hawaii_climate_products_container/preliminary/ignition_prob/code/day/generate_api.py mn $CUSTOM_DATE
python3 -W ignore /home/hawaii_climate_products_container/preliminary/ignition_prob/code/day/generate_api.py oa $CUSTOM_DATE

echo "[task.sh] [4/5] Running map workflow, all counties"
python3 -W ignore /home/hawaii_climate_products_container/preliminary/ignition_prob/code/day/generate_ignition_map.py bi $CUSTOM_DATE
python3 -W ignore /home/hawaii_climate_products_container/preliminary/ignition_prob/code/day/generate_ignition_map.py ka $CUSTOM_DATE
python3 -W ignore /home/hawaii_climate_products_container/preliminary/ignition_prob/code/day/generate_ignition_map.py mn $CUSTOM_DATE
python3 -W ignore /home/hawaii_climate_products_container/preliminary/ignition_prob/code/day/generate_ignition_map.py oa $CUSTOM_DATE

echo "[task.sh] [5/5] Creating statewide mosaic."
python3 -W ignore /home/hawaii_climate_products_container/preliminary/ignition_prob/code/day/statewide_mosaic.py