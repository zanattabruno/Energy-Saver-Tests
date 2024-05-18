#!/bin/bash
helm ls --all --short -n ricxapp | grep xapp | xargs -L1 helm uninstall -n ricxapp &
helm ls --all --short -n ricplt | grep e2node | xargs -L1 helm uninstall -n ricplt &
helm ls --all --short -n ricplt | grep e2term | xargs -L1 helm uninstall -n ricplt &
helm ls --all --short -n ricrapp | grep rapp | xargs -L1 helm uninstall -n ricrapp &
kubectl delete -f envmanager -n ricplt