import os
import json
import logging
from kafka import KafkaConsumer

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

TOPIC_NAME = os.getenv("KAFKA_TOPIC")
KAFKA_BROKER = os.getenv("KAFKA_BROKER_URL")

GROUP_ID = "post_consumer_group"

def main():
    log.info(f"Connecting to Kafka broker at {KAFKA_BROKER}, topic: {TOPIC_NAME}")

    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset="earliest",
        group_id=GROUP_ID,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )

    log.info("Starting Post Consumer...")
    for message in consumer:
        post = message.value
        log.info(f"Consumed post: {post}")

if __name__ == "__main__":
    main()