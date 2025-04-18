#!/bin/bash
echo "Cleaning..."
bash remove_opt.sh 

echo "Restarting Near-RT RIC..." &&
kubectl rollout restart statefulset statefulset-ricplt-dbaas-server -n ricplt &
kubectl rollout restart deployment deployment-ricplt-a1mediator -n ricplt &
kubectl rollout restart deployment deployment-ricplt-alarmmanager -n ricplt &
kubectl rollout restart deployment deployment-ricplt-appmgr -n ricplt &
kubectl rollout restart deployment deployment-ricplt-e2mgr -n ricplt &
kubectl rollout restart deployment deployment-ricplt-o1mediator -n ricplt &
kubectl rollout restart deployment deployment-ricplt-rtmgr -n ricplt &
kubectl rollout restart deployment deployment-ricplt-submgr -n ricplt &
kubectl rollout restart deployment deployment-ricplt-vespamgr -n ricplt & 
kubectl rollout restart deployment r4-infrastructure-prometheus-server  -n ricplt &
kubectl rollout restart deployment r4-infrastructure-prometheus-alertmanager -n ricplt

echo "Restarting Non-RT RIC..." &&
kubectl rollout restart deployment a1controller -n nonrtric &
kubectl rollout restart deployment capifcore -n nonrtric &
kubectl rollout restart deployment controlpanel -n nonrtric &
kubectl rollout restart deployment db -n nonrtric &
kubectl rollout restart deployment nonrtricgateway -n nonrtric &
kubectl rollout restart deployment orufhrecovery -n nonrtric &
kubectl rollout restart deployment ransliceassurance -n nonrtric &
kubectl rollout restart deployment rappcatalogueenhancedservice -n nonrtric &
kubectl rollout restart deployment rappcatalogueservice -n nonrtric &
kubectl rollout restart statefulset a1-sim-osc -n nonrtric &
kubectl rollout restart statefulset a1-sim-std -n nonrtric &
kubectl rollout restart statefulset a1-sim-std2 -n nonrtric &
kubectl rollout restart statefulset dmaapadapterservice -n nonrtric &
kubectl rollout restart statefulset dmaapmediatorservice -n nonrtric &
kubectl rollout restart statefulset helmmanager -n nonrtric &&
kubectl delete pvc helmmanager-vardata-helmmanager-0 -n nonrtric &
kubectl rollout restart statefulset informationservice -n nonrtric &&
kubectl delete pvc informationservice-vardata-informationservice-0 -n nonrtric &
kubectl rollout restart statefulset policymanagementservice -n nonrtric &&
kubectl delete pvc policymanagementservice-vardata-policymanagementservice-0 -n nonrtric

echo "Restarting SMO" &&
kubectl rollout restart deployment chronograf-chronograf -n smo &
kubectl rollout restart deployment influxdb-connector -n smo &
kubectl rollout restart deployment kafdrop -n smo &
kubectl rollout restart deployment ves-collector -n smo &
kubectl rollout restart statefulset influxdb  -n smo &&
kubectl delete pvc influxdb-data-influxdb-0 -n smo &
kubectl rollout restart statefulset kafka  -n smo &&
kubectl delete pvc data-kafka-0 -n smo &
kubectl rollout restart statefulset kafka-zookeeper  -n smo &&
kubectl delete pvc data-kafka-zookeeper-0 -n smo