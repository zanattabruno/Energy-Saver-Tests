#!/bin/bash
curl -v -X POST "http://10.43.0.228:31003/restconf/operations/handover" -H "Content-Type: application/json" -d @scripts/handover_payload.json