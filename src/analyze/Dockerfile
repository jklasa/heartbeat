FROM python:3.10

RUN apt-get update && \
    apt-get install --no-install-recommends --yes \
        librdkafka-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY ./analyze/requirements.txt ./

RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt && \
    rm -rf /tmp/*

COPY ./common ./common
COPY ./tweet ./tweet 
COPY ./analyze ./

CMD ["sleep", "infinity"]
#CMD ["python3", "./analyze.py", "--config", "/etc/config/analyze.yaml"]

