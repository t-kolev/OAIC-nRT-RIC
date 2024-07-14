#!/bin/bash
# fail on error
set -eux
pod=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=a1mediator,app.kubernetes.io/instance=a1" -o jsonpath="{.items[0].metadata.name}")
# this listener must run to forward the port, it's not just a config change
# it logs a line periodically that don't add much value, capture in a file.
rm forward.log
kubectl port-forward "$pod" 10000:10000 > forward.log 2>&1  &
