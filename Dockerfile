FROM python:3-alpine

COPY code/requirements.txt /opt/nuvlabox/

RUN pip install -r /opt/nuvlabox/requirements.txt \
    && rm -rf /var/cache/apt/* 

COPY code/ /opt/nuvlabox/

WORKDIR /opt/nuvlabox/

# ENTRYPOINT ["python", "manager.py"]
