#!/bin/bash

set -e

CLUSTER_NAME="my-cluster"
KIND_CONFIG="./kind/config.yaml"

POST_PUSHER_IMAGE="post-pusher:v1"
POST_CONSUMER_IMAGE="post-consumer:v1"

echo "=== Création du cluster Kind ==="
if kind get clusters | grep -q "$CLUSTER_NAME"; then
  echo "Cluster $CLUSTER_NAME déjà existant"
else
  kind create cluster --config "$KIND_CONFIG" --name "$CLUSTER_NAME"
fi

echo "=== Vérification des nodes ==="
kubectl get nodes

echo "=== Déploiement Kafka ==="
kubectl apply -f ./kafka/deployment.yaml
kubectl apply -f ./kafka/service.yaml

kubectl wait --for=condition=available deployment/kafka-broker --timeout=120s

echo "=== Déploiement ConfigMap UI ==="
kubectl apply -f ./ui/config.yaml

if ! kubectl get secret gcp-key-secret >/dev/null 2>&1; then
  echo "=== Création du secret GCP ==="
  kubectl create secret generic gcp-key-secret \
    --from-file=key.json=./service-account.json
else
  echo "Secret GCP déjà existant"
fi

echo "=== Build et chargement du post_pusher ==="
cd post_pusher
docker build -t "$POST_PUSHER_IMAGE" .
cd ..
kind load docker-image "$POST_PUSHER_IMAGE" --name "$CLUSTER_NAME"

kubectl apply -f ./post_pusher/deployment.yaml

kubectl wait --for=condition=available deployment/post-pusher-kafka --timeout=120s

echo "=== Build et chargement du post_consumer ==="
cd post_consumer
docker build -t "$POST_CONSUMER_IMAGE" .
cd ..
kind load docker-image "$POST_CONSUMER_IMAGE" --name "$CLUSTER_NAME"

kubectl apply -f ./post_consumer/deployment.yaml

kubectl wait --for=condition=available deployment/post-consumer-kafka --timeout=120s

echo "=== Scale des consumers à 3 ==="
kubectl scale deployment post-consumer-kafka --replicas=3

echo "=== Déploiement Kafka UI ==="
kubectl apply -f ./ui/deployment.yaml
kubectl apply -f ./ui/service.yaml

echo "=== État des pods ==="
kubectl get pods

echo "=== Projet démarré avec succès ==="
echo "Kafka UI accessible via :"
echo "kubectl port-forward svc/kafka-ui-service 8080:8080 --address 0.0.0.0"