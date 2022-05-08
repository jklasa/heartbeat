FROM python:3.10

RUN apt-get update && \
    apt-get install --no-install-recommends --yes \
        librdkafka-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY ./idb/requirements.txt ./

RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt && \
    rm -rf /tmp/*

COPY ./common ./common
COPY ./idb ./

CMD ["sleep", "infinity"]
#CMD ["python3", "./transfer.py", "--config", "/etc/config/idb.yaml"]

