FROM python:3.7-slim-buster

COPY code/requirements.txt /opt/nuvlabox/

RUN apt update && apt install g++ libbluetooth-dev libboost-all-dev libglib2.0-dev pkg-config -y && pip install -r /opt/nuvlabox/requirements.txt && rm -rf /var/cache/apt/* 

COPY code/ /opt/nuvlabox/

WORKDIR /opt/nuvlabox/

ENTRYPOINT ["python", "manager.py"]
