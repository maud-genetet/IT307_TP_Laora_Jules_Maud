import logging
import random
import os
import json
import re
import time
import argparse
from kafka import KafkaProducer


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


TOPIC = os.getenv("KAFKA_TOPIC")  # Name of the Kafka topic
KAFKA_BROKER = os.getenv("KAFKA_BROKER_URL")  # Address of the Kafka broker

BATCH_SIZE = 2 # 50  # Number of posts to process in each batch

# Liste simple des champs autorisés 
ALLOWED_FIELDS = {
    'id', 'post_type_id', 'accepted_answer_id', 'creation_date',
    'score', 'view_count', 'body', 'owner_user_id',
    'last_editor_user_id', 'last_edit_date', 'last_activity_date',
    'title', 'tags', 'answer_count', 'comment_count',
    'content_license', 'parent_id'
}

def transform_key(key):
    # Remove '@' and convert to snake_case
    key = key.replace('@', '')
    key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
    return key

def filter_post(post, allowed_columns):
    return {k: v for k, v in post.items() if k in allowed_columns}

def transform_and_filter_post(post, allowed_columns):
    transformed_post = {transform_key(k): v for k, v in post.items()}
    filtered_post = filter_post(transformed_post, allowed_columns)
    return filtered_post


def post_kafka(transformed_post, kafka_host):
    # Kafka configuration
    bootstrap_servers = [kafka_host]

    # Create Producer instance
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    try:
        # Produce and send a single message
        future = producer.send(TOPIC, transformed_post)
        record_metadata = future.get(timeout=10)
        print(f"Message delivered to {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")
    except Exception as e:
        print(f"Message delivery failed: {e}")
    finally:
        producer.close()

def main(kafka_host):
    # Load the post from the JSON file
    data_filepath = "./data/movies-stackexchange/json/posts.json"
    log.info(data_filepath)
    log.info(os.getcwd())
    with open(data_filepath, "r") as f:
        content = f.read()
    posts = json.loads(content)

    for i in range(BATCH_SIZE):
        post = random.choice(posts)

        allowed_columns = ALLOWED_FIELDS
        # Transform the post for insertion and save to a temporary JSON file
        transformed_post = transform_and_filter_post(post, allowed_columns)
        
        post_kafka(transformed_post, kafka_host)

        time.sleep(10)

# Main execution
if __name__ == "__main__":

    main(
        kafka_host=KAFKA_BROKER
    )