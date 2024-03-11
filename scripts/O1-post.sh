#!/bin/bash

# Define o URL do endpoint REST
URL="http://e2node1-e2sim-helm-o1.ricplt:8090/restconf/operations/tx-gain"

# Define o JSON payload para o corpo da solicitação
PAYLOAD='{"gain":1.25}'

# Usa o comando cURL para enviar uma solicitação POST para o URL com o payload JSON
curl -v "$URL" -H "Accept: application/json" -H "Content-Type: application/json" -d "$PAYLOAD"
