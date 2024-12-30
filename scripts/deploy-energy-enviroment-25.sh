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

helm upgrade --install e2node5 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=5 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node6 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=6 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node7 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=7 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node8 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=8 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node9 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=9 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node10 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=10 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node11 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=11 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node12 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=12 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node13 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=13 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node14 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=14 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node15 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=15 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node16 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=16 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node17 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=17 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node18 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=18 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node19 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=19 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node20 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=20 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node21 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=21 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade--install e2node22 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=22 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node23 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=23 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node24 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=24 \
    --set image.args.port=30001 \
    -n ricplt --wait

helm upgrade --install e2node25 ../helm-charts/e2sim-helm \
    --set image.args.e2term=10.43.0.225 \
    --set image.args.mcc=724 \
    --set image.args.mnc=011 \
    --set image.args.nodebid=25 \
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

helm upgrade --install xappmonitoring5 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="5" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring6 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="6" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring7 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="7" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring8 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="8" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring9 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="9" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring10 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="10" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring11 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="11" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring12 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="12" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring13 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="13" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring14 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="14" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring15 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="15" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring16 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="16" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring17 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="17" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring18 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="18" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring19 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="19" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring20 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="20" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring21 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="21" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring22 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="22" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring23 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="23" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring24 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="24" \
    -n ricxapp --wait

helm upgrade --install xappmonitoring25 ../helm-charts/bouncer-xapp \
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
    --set containers[0].args[5]="25" \
    -n ricxapp --wait

helm upgrade --install handover-xapp ../helm-charts/handover-xapp -n ricxapp --wait

kubectl apply -f envmanager -n ricplt

sleep 45

helm upgrade --install energy-saver-rapp ../helm-charts/energy-saver-rapp -n ricrapp --wait
