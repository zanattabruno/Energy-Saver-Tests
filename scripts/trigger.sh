#!/bin/bash
#curl -X POST http://localhost:5000/deployment-map -H "Content-Type: application/json" -d @scripts/deployment-map.json
curl -X POST http://ric-o-smo-app-ric-o-smoapp.smo.svc.cluster.local/deployment-map -H "Content-Type: application/json" -d @scripts/deployment-map.json