FROM python:3.9-alpine3.12 as builder
# because of pybluez[ble] which requires gattlib, the dependencies are quite a few unstable for RPi
# for the future, consider using bluepy instead - which requires privileged access, and does not provide very detailed
#     information about BLE devices, becoming nuisance to the user

COPY code/requirements.txt /opt/nuvlabox/

RUN apk update && apk add --no-cache g++ bluez-dev

RUN pip install -r /opt/nuvlabox/requirements.txt

# ======= #

FROM python:3.9-alpine3.12

ARG GIT_BRANCH
ARG GIT_COMMIT_ID
ARG GIT_BUILD_TIME
ARG GITHUB_RUN_NUMBER
ARG GITHUB_RUN_ID
ARG PROJECT_URL

LABEL git.branch=${GIT_BRANCH}
LABEL git.commit.id=${GIT_COMMIT_ID}
LABEL git.build.time=${GIT_BUILD_TIME}
LABEL git.run.number=${GITHUB_RUN_NUMBER}
LABEL git.run.id=${GITHUB_RUN_ID}
LABEL org.opencontainers.image.authors="support@sixsq.com"
LABEL org.opencontainers.image.created=${GIT_BUILD_TIME}
LABEL org.opencontainers.image.url=${PROJECT_URL}
LABEL org.opencontainers.image.vendor="SixSq SA"
LABEL org.opencontainers.image.title="NuvlaBox Peripheral Manager Bluetooth"
LABEL org.opencontainers.image.description="Identifies bluetooth devices in the vicinity of the NuvlaBox"

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

COPY code/ LICENSE /opt/nuvlabox/

RUN apk add --no-cache bluez-dev

WORKDIR /opt/nuvlabox/

ONBUILD RUN ./license.sh

ENTRYPOINT ["python", "-u", "manager.py"]
