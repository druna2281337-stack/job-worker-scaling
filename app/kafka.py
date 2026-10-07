import json

from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="kafka:29092",
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
)


def publish_job(job_id: str, duration_seconds: int):
    producer.send(
        "jobs",
        key=job_id.encode("utf-8"),
        value={
            "job_id": job_id,
            "duration_seconds": duration_seconds,
        },
    )

    producer.flush()
