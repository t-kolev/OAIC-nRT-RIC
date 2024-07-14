#!/bin/sh
echo "\n\n a1" > log.txt
kubectl get pods --namespace=default | awk '{ print $1 }' | egrep '^a1-a1mediator-' | xargs kubectl logs -p >> log.txt 2>&1
kubectl get pods --namespace=default | awk '{ print $1 }' | egrep '^a1-a1mediator-' | xargs kubectl logs  >> log.txt 2>&1

echo "\n\n test receiver" >> log.txt
# the -p gets the "previous logs" in case the prior container crashed.. very useful for debugging a new receiver.
kubectl get pods --namespace=default | awk '{ print $1 }' | egrep '^testreceiver-' | xargs -I X kubectl logs -p X testreceiver  >> log.txt 2>&1
kubectl get pods --namespace=default | awk '{ print $1 }' | egrep '^testreceiver-' | xargs -I X kubectl logs X testreceiver  >> log.txt 2>&1

echo "\n\n delay" >> log.txt
kubectl get pods --namespace=default | awk '{ print $1 }' | egrep '^testreceiver-' | xargs -I X kubectl logs -p X delayreceiver  >> log.txt 2>&1
kubectl get pods --namespace=default | awk '{ print $1 }' | egrep '^testreceiver-' | xargs -I X kubectl logs X delayreceiver  >> log.txt 2>&1

echo "\n\n query" >> log.txt
kubectl get pods --namespace=default | awk '{ print $1 }' | egrep '^testreceiver-' | xargs -I X kubectl logs -p X queryreceiver  >> log.txt 2>&1
kubectl get pods --namespace=default | awk '{ print $1 }' | egrep '^testreceiver-' | xargs -I X kubectl logs X queryreceiver  >> log.txt 2>&1

echo "\n\n sdl-redis" >> log.txt
kubectl get pods --namespace=default | awk '{ print $1 }' | egrep '^redis-standalone' | xargs kubectl logs  >> log.txt 2>&1
