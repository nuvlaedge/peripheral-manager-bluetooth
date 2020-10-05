FROM python:3.6-slim

COPY code/requirements.txt /opt/nuvlabox/

RUN apt update && apt install g++ libbluetooth-dev libboost-all-dev libglib2.0-dev pkg-config -y && pip install -r /opt/nuvlabox/requirements.txt && rm -rf /var/cache/apt/*

COPY code/ LICENSE /opt/nuvlabox/

WORKDIR /opt/nuvlabox/

ONBUILD RUN ./license.sh

# ENTRYPOINT ["python", "manager.py"]
docker run -v --cap-add=SYS_ADMIN -v /opt/bluetooth:/var/lib/bluetooth -v /sys/fs/cgroup:/sys/fs/cgroup:ro --net=host -it python:3.6-slim bash
