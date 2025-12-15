# TP Noté Projet

**Participants** : Laora Aimi, Jules Maulard, Maud Genetet

Ce document décrit pas à pas la mise en place complète du projet : création du cluster Kubernetes avec Kind, déploiement de Kafka, des producteurs et consommateurs, intégration BigQuery, Kafka UI et DBT.

---

## 1. Création du cluster Kubernetes (Kind)

Depuis le dossier `kind/` :

```bash
kind create cluster --config ./kind/config.yaml --name my-cluster
```

### Suppression de clusters existants (si ports déjà utilisés)

Lister les clusters :

```bash
kind get clusters
```

Supprimer un cluster précis :

```bash
kind delete cluster --name <cluster-name>
```

Ou supprimer tous les clusters :

```bash
kind delete clusters --all
```

### Vérification du cluster

```bash
kubectl get nodes
```

On doit voir **1 master** et **3 workers**.

---

## 2. Mise en place de Kafka

### Déploiement du broker Kafka

```bash
kubectl apply -f ./kafka/deployment.yaml
```

### Déploiement du service Kafka

```bash
kubectl apply -f ./kafka/service.yaml
```

### Vérification

```bash
kubectl get pods
```

Un pod du type suivant doit être présent :

```
kafka-broker-xxxxxxxxxx-xxxxx
```

---

## 3. Configuration via ConfigMap

### Déploiement de la ConfigMap

```bash
kubectl apply -f ./ui/config.yaml
```

### Vérification

```bash
kubectl get configmaps
```

On doit voir :

* `kafka-ui-config`
* une ConfigMap système créée automatiquement par Kubernetes

### Ajout du secret GCP (BigQuery)

Ajout de la clé du service account utilisée par les consumers pour écrire dans BigQuery :

```bash
kubectl create secret generic gcp-key-secret \
  --from-file=key.json=./service-account.json
```

---

## 4. Déploiement du producer `post_pusher`

### Modification du code Python

Dans `post_pusher/main.py`, utilisation des variables d’environnement issues de la ConfigMap :

```python
TOPIC = os.getenv("KAFKA_TOPIC")
KAFKA_BROKER = os.getenv("KAFKA_BROKER_URL")
```

### Build de l’image Docker

```bash
cd post_pusher
docker build -t post-pusher:v1 .
cd ..
```

### Chargement de l’image dans Kind

```bash
kind load docker-image post-pusher:v1 --name my-cluster
```

### Déploiement Kubernetes

```bash
kubectl apply -f ./post_pusher/deployment.yaml
```

### En cas d’erreur (déploiement existant)

```bash
kubectl delete deployment post-pusher-kafka
```

### Vérification

```bash
kubectl get pods
```

Suivi des logs :

```bash
kubectl logs -f <nom-du-pod>
```

---

## 5. Déploiement des consumers Kafka

### Build de l’image consumer

```bash
cd post_consumer
docker build -t post-consumer:v1 .
cd ..
```

### Chargement de l’image dans Kind

```bash
kind load docker-image post-consumer:v1 --name my-cluster
```

### Déploiement Kubernetes

```bash
kubectl apply -f post_consumer/deployment.yaml
```

### Vérification de la réception des messages

```bash
kubectl logs -f -l app=post-consumer-kafka
```

### Passage à 3 consumers

```bash
kubectl scale deployment post-consumer-kafka --replicas=3
```

Vérification :

```bash
kubectl get pods
```

Logs de tous les consumers :

```bash
kubectl logs -f -l app=post-consumer-kafka --prefix
```

---

## 6. Envoi des données dans BigQuery

### Création du dataset et de la table

Depuis `gcp/BigQuery/`, exécuter la requête suivante :

```sql
CREATE SCHEMA IF NOT EXISTS `coursbigquery-477209.tp_kafka`;

CREATE TABLE `coursbigquery-477209.tp_kafka.posts` (
  id STRING NOT NULL,
  post_type_id STRING NOT NULL,
  accepted_answer_id STRING,
  creation_date TIMESTAMP NOT NULL,
  score INTEGER NOT NULL,
  view_count INTEGER,
  body STRING NOT NULL,
  owner_user_id STRING,
  last_editor_user_id STRING,
  last_edit_date TIMESTAMP,
  last_activity_date TIMESTAMP,
  title STRING,
  tags STRING,
  answer_count INTEGER,
  comment_count INTEGER NOT NULL,
  content_license STRING NOT NULL,
  parent_id STRING
);
```

Le dataset `tp_kafka` doit apparaître dans BigQuery.

### Mise à jour de la ConfigMap

Ajouter :

```
coursbigquery-477209.tp_kafka
```

Dans `ui/config.yaml`, puis réappliquer :

```bash
kubectl apply -f ./ui/config.yaml
```

---

## 7. Kafka UI

### Déploiement

```bash
kubectl apply -f ./ui/deployment.yaml
kubectl apply -f ./ui/service.yaml
```

### Accès à l’interface

```bash
kubectl port-forward svc/kafka-ui-service 8080:8080 --address 0.0.0.0
```

Penser à faire le **port-forward GCP vers la machine locale** si nécessaire.

Accès via navigateur :

```
http://localhost:8080
```

---

## 8. DBT (BigQuery)

### Installation

```bash
pip install dbt-bigquery
```

### Initialisation du projet

```bash
dbt init mon_projet_data
```

### Création du modèle SQL

Créer un fichier `.sql` dans :

```
mon_projet_dbt/models/
```

### Exécution

```bash
dbt run
```

La table générée apparaît alors dans BigQuery.

---

## 9. Nettoyage complet

### Suppression totale du cluster

```bash
kind delete clusters --all
```
