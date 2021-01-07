FROM python:3.9-alpine as builder
# because of pybluez[ble] which requires gattlib, the dependencies are quite a few unstable for RPi
# for the future, consider using bluepy instead - which requires privileged access, and does not provide very detailed
#     information about BLE devices, becoming nuisance to the user

COPY code/requirements.txt /opt/nuvlabox/

RUN apk update && apk add --no-cache g++ bluez-dev

RUN pip install -r /opt/nuvlabox/requirements.txt

# ======= #

FROM python:3.9-alpine

ARG GIT_BRANCH
ARG GIT_COMMIT_ID
ARG GIT_BUILD_TIME
ARG GITHUB_RUN_NUMBER
ARG GITHUB_RUN_ID

LABEL git.branch=${GIT_BRANCH}
LABEL git.commit.id=${GIT_COMMIT_ID}
LABEL git.build.time=${GIT_BUILD_TIME}
LABEL git.run.number=${GITHUB_RUN_NUMBER}
LABEL git.run.id=${TRAVIS_BUILD_WEB_URL}

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

COPY code/ LICENSE /opt/nuvlabox/

RUN apk add --no-cache bluez-dev

WORKDIR /opt/nuvlabox/

ONBUILD RUN ./license.sh

ENTRYPOINT ["python", "-u", "manager.py"]
