# Job Worker Scaling

Pet project demonstrating background job processing and horizontal worker scaling.

## Stack

- Python
- FastAPI
- Kafka
- PostgreSQL
- Docker Compose
- Prometheus
- Grafana

## How it works

FastAPI provides a REST API for creating and checking jobs.

When a job is created:

1. FastAPI stores the job in PostgreSQL.
2. FastAPI sends the job to Kafka.
3. Workers consume jobs from Kafka.
4. A worker processes the job.
5. The worker updates the job status in PostgreSQL.

Job statuses:

- queued
- processing
- completed
- failed

Prometheus collects job metrics.

Grafana visualizes:

- queued jobs
- processing jobs
- completed jobs

The number of workers can be horizontally scaled with Docker Compose.

## Run

Build and start the project:

```bash
docker compose up -d --build
Run with one worker:
docker compose up -d --scale worker=1
Run with three workers:
docker compose up -d --scale worker=3
Services
FastAPI Swagger:
http://localhost:8000/docs
Prometheus:
http://localhost:9090
Grafana:
http://localhost:3000
Grafana datasource and the JobFlow dashboard are provisioned automatically.
