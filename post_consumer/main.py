import os
import json
import logging
from kafka import KafkaConsumer
from google.cloud import bigquery

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

TOPIC_NAME = os.getenv("KAFKA_TOPIC")
KAFKA_BROKER = os.getenv("KAFKA_BROKER_URL")

GROUP_ID = "post_consumer_group"

BQTABLE_ID = os.getenv("BIGQUERY_TABLE_ID")

def main():
    log.info(f"Connecting to Kafka broker at {KAFKA_BROKER}, topic: {TOPIC_NAME}")

    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset="earliest",
        group_id=GROUP_ID,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )

    bq_client = bigquery.Client()

    log.info("Starting Post Consumer...")
    for message in consumer:
        post = message.value
        raw_to_insert = [post]
        errors = bq_client.insert_rows_json(BQTABLE_ID, raw_to_insert)
        if errors == []:
            log.info(f"Inserted post into BigQuery: {post}")
        else:
            log.error(f"Failed to insert post into BigQuery: {errors}")

if __name__ == "__main__":
    main()