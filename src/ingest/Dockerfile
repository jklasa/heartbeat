FROM python:3.10

RUN apt-get update && \
    apt-get install --no-install-recommends --yes \
        librdkafka-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY ./ingest/requirements.txt ./

RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY ./common ./common
COPY ./ingest ./

CMD ["sleep", "infinity"]
#CMD ["python3", "./ingest.py", "--config", "/etc/config/ingest.yaml"]


# NEEDS ENVIRONMENT VARS:
#   * BEARER_TOKEN
