#!/bin/bash

# Base URL to be fetched
BASE_URL="http://service-ricxapp-xappmonitoring"

# Print headers for Excel
echo -e "Monitoring Instance\tTime to Connect (s)\tTime to Start Transfer (s)\tTotal Time (s)\tElapsed Time (s)\tStatus Code"

# Loop through monitoring instances 1 to 4
for i in {1..4}
do
  URL="${BASE_URL}${i}-prometheus.ricxapp:9090/metrics"

  # Measure the time taken by the curl command
  start_time=$(date +%s.%N)
  curl_output=$(curl -o scrape-output${i}.txt -s -w "%{time_connect}\t%{time_starttransfer}\t%{time_total}\t%{http_code}" $URL)
  end_time=$(date +%s.%N)

  # Calculate elapsed time
  elapsed_time=$(echo "$end_time - $start_time" | bc)
  sync
  # Check if scrape-output.txt is empty
  if [ ! -s scrape-output.txt ]; then
    echo "Warning: scrape-output${i}.txt is empty for Monitoring${i}. URL: $URL"
  fi

  # Print the results for this instance in tab-separated format
  echo -e "Monitoring${i}\t$curl_output\t$elapsed_time"
done
