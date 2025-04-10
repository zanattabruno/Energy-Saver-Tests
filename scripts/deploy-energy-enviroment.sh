#!/bin/bash

#This command must be run inside scripts folder

python3 deploy-e2term.py 

bash policy_enode_ue/create_policy_type.bash

helm upgrade --install e2node1 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=1 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node2 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=2 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node3 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=3 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node4 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=4 \
    --set image.args.port=30001 \
    -n ricplt --wait

sleep 10

helm upgrade --install xappmonitoring1 ../helm-charts/bouncer-xapp \
    --set containers[0].image.name="zanattabruno/bouncer-rc" \
    --set containers[0].image.registry="registry.hub.docker.com" \
    --set containers[0].image.tag="TNSM-24" \
    --set containers[0].name="bouncer-xapp" \
    --set containers[0].command[0]="b_xapp_main" \
    --set containers[0].args[0]="--mcc" \
    --set containers[0].args[1]="724" \
    --set containers[0].args[2]="--mnc" \
    --set containers[0].args[3]="011" \
    --set containers[0].args[4]="--nodebid" \
    --set containers[0].args[5]="1" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring2 ../helm-charts/bouncer-xapp \
    --set containers[0].image.name="zanattabruno/bouncer-rc" \
    --set containers[0].image.registry="registry.hub.docker.com" \
    --set containers[0].image.tag="TNSM-24" \
    --set containers[0].name="bouncer-xapp" \
    --set containers[0].command[0]="b_xapp_main" \
    --set containers[0].args[0]="--mcc" \
    --set containers[0].args[1]="724" \
    --set containers[0].args[2]="--mnc" \
    --set containers[0].args[3]="011" \
    --set containers[0].args[4]="--nodebid" \
    --set containers[0].args[5]="2" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring3 ../helm-charts/bouncer-xapp \
    --set containers[0].image.name="zanattabruno/bouncer-rc" \
    --set containers[0].image.registry="registry.hub.docker.com" \
    --set containers[0].image.tag="TNSM-24" \
    --set containers[0].name="bouncer-xapp" \
    --set containers[0].command[0]="b_xapp_main" \
    --set containers[0].args[0]="--mcc" \
    --set containers[0].args[1]="724" \
    --set containers[0].args[2]="--mnc" \
    --set containers[0].args[3]="011" \
    --set containers[0].args[4]="--nodebid" \
    --set containers[0].args[5]="3" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring4 ../helm-charts/bouncer-xapp \
    --set containers[0].image.name="zanattabruno/bouncer-rc" \
    --set containers[0].image.registry="registry.hub.docker.com" \
    --set containers[0].image.tag="TNSM-24" \
    --set containers[0].name="bouncer-xapp" \
    --set containers[0].command[0]="b_xapp_main" \
    --set containers[0].args[0]="--mcc" \
    --set containers[0].args[1]="724" \
    --set containers[0].args[2]="--mnc" \
    --set containers[0].args[3]="011" \
    --set containers[0].args[4]="--nodebid" \
    --set containers[0].args[5]="4" \
    -n ricxapp --wait

helm upgrade --install handover-xapp ../helm-charts/handover-xapp -n ricxapp --wait

kubectl apply -f envmanager -n ricplt

sleep 45

helm upgrade --install energy-saver-rapp ../helm-charts/energy-saver-rapp -n ricrapp --wait
