#!/bin/bash

# Description:
# This script retrieves logs from a Kubernetes pod whose name starts with 'energy-saver-rapp'
# and saves the logs to a .log file with the current datetime in the filename.

# Retrieve the name of the pod that starts with 'energy-saver-rapp'
POD_NAME=$(kubectl get pods --no-headers -o custom-columns=":metadata.name" | grep '^energy-saver-rapp' | head -n 1)

# Check if a pod name was found
if [ -z "$POD_NAME" ]; then
  echo "No pod found with a name starting with 'energy-saver-rapp'."
  exit 1
fi

echo "Fetching logs from pod: $POD_NAME"

# Get the current datetime for the log filename
CURRENT_DATETIME=$(date '+%Y%m%d-%H%M%S')

# Define the log filename
LOG_FILENAME="logs_${POD_NAME}_${CURRENT_DATETIME}.log"

# Retrieve the logs from the identified pod and save to file
kubectl logs "$POD_NAME" > "$LOG_FILENAME"

echo "Logs have been saved to: $LOG_FILENAME"