FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sleep", "infinity"]
#CMD ["python3", "./analyze.py", "--config", "/etc/config/analyze.yaml"]

