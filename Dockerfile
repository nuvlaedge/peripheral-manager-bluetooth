FROM python:3-buster

COPY code/requirements.txt /opt/nuvlabox/

RUN apt update && apt install libbluetooth-dev -y

RUN pip install -r /opt/nuvlabox/requirements.txt

RUN rm -rf /var/cache/apt/*

COPY code/ /opt/nuvlabox/

WORKDIR /opt/nuvlabox/

# ENTRYPOINT ["python", "manager.py"]
