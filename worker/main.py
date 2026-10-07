import json
import time

from kafka import KafkaConsumer

from app.database import SessionLocal, init_db
from app.models import Job


def process_job(job_id: str, duration_seconds: int):
    db = SessionLocal()

    try:
        job = db.get(Job, job_id)

        if job is None:
            print(f"Job {job_id} not found")
            return

        job.status = "processing"
        db.commit()

        print(
            f"Processing {job_id} "
            f"for {duration_seconds} seconds..."
        )

        time.sleep(duration_seconds)

        job.status = "completed"
        job.result = "Job successfully processed"

        db.commit()

        print(f"Completed {job_id}")

    except Exception as exc:
        db.rollback()

        job = db.get(Job, job_id)

        if job:
            job.status = "failed"
            job.result = str(exc)
            db.commit()

        print(f"Job {job_id} failed: {exc}")

    finally:
        db.close()


def main():
    init_db()

    consumer = KafkaConsumer(
        "jobs",
        bootstrap_servers="kafka:29092",
        group_id="jobflow-workers",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda value: json.loads(
            value.decode("utf-8")
        ),
    )

    print("Worker started and waiting for jobs...")

    for message in consumer:
        data = message.value

        process_job(
            job_id=data["job_id"],
            duration_seconds=data["duration_seconds"],
        )

        consumer.commit()


if __name__ == "__main__":
    main()
