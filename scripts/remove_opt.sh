#!/bin/bash
helm ls --all --short -n ricxapp | grep xapp | xargs -L1 helm uninstall -n ricxapp
helm ls --all --short -n ricplt | grep e2node | xargs -L1 helm uninstall -n ricplt
helm ls --all --short -n ricplt | grep e2term | xargs -L1 helm uninstall -n ricplt

kubectl delete -f experiment.yaml -n ricplt