#!/usr/bin/env bash

# Filename: get_energy_saver_logs.sh
# Description: Retrieve logs from the first pod that starts with "energy-saver-rapp"
#              and save them to a file named with the current timestamp.

# Find the pod name (takes the first match if multiple).
POD_NAME=$(kubectl get pods --no-headers \
  | grep -m 1 '^energy-saver-rapp' \
  | awk '{print $1}')

# (Optional) Check if we found a pod.
if [[ -z "${POD_NAME}" ]]; then
  echo "No pod found starting with 'energy-saver-rapp'. Exiting."
  exit 1
fi

# Generate a timestamp (format: YYYYMMDD_HHMMSS).
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create the log filename using the timestamp.
LOG_FILENAME="energy-saver-rapp-${TIMESTAMP}.log"

# Retrieve logs from the pod and save to the file.
kubectl logs "${POD_NAME}" > "${LOG_FILENAME}"

echo "Logs saved to ${LOG_FILENAME}"
