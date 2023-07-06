FROM python:3-alpine

ENV VERSION=1.0.0

LABEL maintainer="Patrick Becker" \
  org.opencontainers.image.url="https://github.com/patbec/pages-base" \
  org.opencontainers.image.version="${VERSION}" \
  org.opencontainers.image.licenses="MIT"

RUN adduser -D python
USER python
WORKDIR /data

ENV PYTHONUNBUFFERED="1"
ENV PYTHONIOENCODING="UTF-8"

ADD ./data/run.py /data/run.py

ARG PIP_PACKAGES="jinja2 jsonschema"
ARG PIP_ROOT_USER_ACTION="ignore"
ARG PIP_PROGRESS_BAR="off"

RUN pip install --no-cache-dir ${PIP_PACKAGES}

EXPOSE 8090

CMD [ "python", "run.py" ]