FROM python:3-alpine

EXPOSE 8090

RUN adduser -D python
USER python
WORKDIR /data

ENV APP_CONFIG_FILE="config.json"

ADD run.py /data/run.py

ARG PIP_PACKAGES="jinja2 jsonschema"
ARG PIP_ROOT_USER_ACTION="ignore"
ARG PIP_PROGRESS_BAR="off"

RUN pip install --no-cache-dir ${PIP_PACKAGES}

CMD [ "python", "run.py" ]