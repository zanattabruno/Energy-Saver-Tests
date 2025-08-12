#!/bin/bash

#This command must be run inside scripts folder

python3 deploy-e2term.py 

bash policy_enode_ue/create_policy_type.bash

BASE_CHART_PATH="../helm-charts/e2sim-helm"
E2TERM_ADDRESS="10.43.0.225"
MCC="724"
MNC="011"
PORT="30001"

# Deploy 25 gNB
for i in {1..25}
do
  helm upgrade --install e2node${i} ${BASE_CHART_PATH} \
    --set image.args.e2term=${E2TERM_ADDRESS} \
    --set image.args.mcc=${MCC} \
    --set image.args.mnc=${MNC} \
    --set image.args.nodebid=${i} \
    --set image.args.port=${PORT} \
    -n ricplt --wait
done

sleep 10

# Configuration
CHART_PATH="../helm-charts/bouncer-xapp"
REGISTRY="registry.hub.docker.com"
IMAGE_NAME="zanattabruno/bouncer-rc"
IMAGE_TAG="TNSM-24"
CONTAINER_NAME="bouncer-xapp"
MCC="724"
MNC="011"
NAMESPACE="ricxapp"

# Loop through 25 instances
for i in {1..25}
do
  helm upgrade --install xappmonitoring${i} "${CHART_PATH}" \
    --set containers[0].image.name="${IMAGE_NAME}" \
    --set containers[0].image.registry="${REGISTRY}" \
    --set containers[0].image.tag="${IMAGE_TAG}" \
    --set containers[0].name="${CONTAINER_NAME}" \
    --set containers[0].command[0]="b_xapp_main" \
    --set containers[0].args[0]="--mcc" \
    --set containers[0].args[1]="${MCC}" \
    --set containers[0].args[2]="--mnc" \
    --set containers[0].args[3]="${MNC}" \
    --set containers[0].args[4]="--nodebid" \
    --set containers[0].args[5]="${i}" \
    -n "${NAMESPACE}" --wait
done

helm upgrade --install handover-xapp ../helm-charts/handover-xapp -n ricxapp --wait

kubectl apply -f envmanager -n ricplt

sleep 45

helm upgrade --install energy-saver-rapp ../helm-charts/energy-saver-rapp -n ricrapp --wait
