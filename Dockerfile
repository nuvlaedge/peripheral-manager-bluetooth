FROM python:3-alpine

COPY code/requirements.txt /opt/nuvlabox/

RUN apk update && apk add libbluetooth-dev pkgconfig glib-dev libgtk-3-devs boost-dev \
    && pip install -r /opt/nuvlabox/requirements.txt \
    && rm -rf /var/cache/apt/* 

COPY code/ /opt/nuvlabox/

WORKDIR /opt/nuvlabox/

ENTRYPOINT ["python", "manager.py"]
