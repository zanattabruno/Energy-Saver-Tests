#!/bin/bash
kubectl rollout restart statefulset statefulset-ricplt-dbaas-server -n ricplt
kubectl rollout restart deployment deployment-ricplt-a1mediator -n ricplt
kubectl rollout restart deployment deployment-ricplt-alarmmanager -n ricplt
kubectl rollout restart deployment deployment-ricplt-appmgr -n ricplt
kubectl rollout restart deployment deployment-ricplt-e2mgr -n ricplt
kubectl rollout restart deployment deployment-ricplt-o1mediator -n ricplt
kubectl rollout restart deployment deployment-ricplt-rtmgr -n ricplt
kubectl rollout restart deployment deployment-ricplt-submgr -n ricplt
kubectl rollout restart deployment deployment-ricplt-vespamgr -n ricplt

kubectl delete -f experiment.yaml -n ricplt