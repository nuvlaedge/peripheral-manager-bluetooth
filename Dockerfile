FROM python:3-slim as builder
# because of pybluez[ble] which requires gattlib, the dependencies are quite a few unstable for RPi
# for the future, consider using bluepy instead - which requires privileged access, and does not provide very detailed
#     information about BLE devices, becoming nuisance to the user

COPY code/requirements.txt /opt/nuvlabox/

RUN apt update && apt install g++ libbluetooth-dev libboost-all-dev libglib2.0-dev pkg-config -y && pip install -r /opt/nuvlabox/requirements.txt && rm -rf /var/cache/apt/*

COPY code/ LICENSE /opt/nuvlabox/

WORKDIR /opt/nuvlabox/

ONBUILD RUN ./license.sh

ENTRYPOINT ["python", "-u", "manager.py"]
