from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

with DAG(
    'kafka_pusher_dag',
    default_args=default_args,
    schedule_interval='@minute',
    catchup=False
) as dag:

    pusher_task = KubernetesPodOperator(
        task_id='push_messages_to_kafka',
        name='post-pusher-job',
        namespace='default', # On lance le pod dans le namespace où est Kafka
        image='post-pusher:v2', # Notre nouvelle image
        image_pull_policy='Never', # Important pour Kind
        
        # On injecte les variables d'environnement
        env_vars={
            'KAFKA_BROKER_URL': 'kafka-broker-service:9092',
            'KAFKA_TOPIC': 'projet-topic',
            'BATCH_SIZE': '20' # On envoie 20 messages par minute
        },
        
        is_delete_operator_pod=True, # Supprime le pod quand c'est fini (propre)
        get_logs=True
    )