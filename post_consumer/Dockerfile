FROM python:3.9.20-slim-bookworm

WORKDIR /app

RUN pip install google-cloud-bigquery kafka-python
ENV PYTHONUNBUFFERED=1

COPY main.py .

CMD ["python", "main.py"]