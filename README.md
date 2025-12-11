# TP Noté Projet : Laora Aimi, Jules Maulard et Maud Genetet

## Création du cluster

Dans `kind/`
Création du cluster avec Kind
```bash
kind create cluster --config ./kind/config.yaml --name my-cluster
```

Si clusters deja existants sur les ports
```bash
kind get clusters
kind delete cluster --name <cluster-name>
```
ou 
```bash
kind delete clusters --all
```

Enfin pour check que nos nodes sont bien crées
```bash
kubectl get nodes
```
et on doit avoir bien nos 3 workers et notre master




## Mise en place de Kafka

Pour deployer le brocker kafka ont fait 
```bash
kubectl apply -f ./kafka/deployment.yaml
```
Puis pour ajouter le service:
```bash
kubectl apply -f ./kafka/service.yaml
```

Pour verifier si ca c'est bien fait:
```bash
kubectl get nodes
```
Je dois avoir mon brocker du type kafka-broker-6758b4c884-rs7fc


## Application de config map

deploiment
```bash
kubectl apply -f ./ui/config.yaml
```

verification:
```bash
kubectl get configmaps
```
on doit avoir kafka-ui-config,
l'autre est normal cré automatiquement (sécurise communication entre pods et kubernetes)


## Deployment du post_pusher

Apres avoir modif le fichier post_pusher/main.py pour utiliser notre ui/config.yaml:
```python
TOPIC = os.getenv("KAFKA_TOPIC")  # Name of the Kafka topic
KAFKA_BROKER = os.getenv("KAFKA_BROKER_URL")  # Address of the Kafka broker
```

deploiment du container post-pusher:v1
```bash
cd post-pusher
docker build -t post-pusher:v1 .
cd ..
```

On deploie maintenant l'image post-pusher dans le cluster:
```bash
kind load docker-image post-pusher:v1 --name my-cluster
```

et enfin deploiment kubernetes, on lui dit de l'utliser
```bash
kubectl apply -f ./post_pusher/deployment.yaml
```

Pour verifier:
```bash
kubectl get pods
```