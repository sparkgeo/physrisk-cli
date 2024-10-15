FROM python:3.10.0-slim as builder
LABEL authors="Sparkgeo UK"

RUN apt-get update && apt-get install -y \
    build-essential \
    libproj-dev \
    proj-data \
    proj-bin \
    python3-scipy \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

ADD app/* /usr/bin/
RUN chmod +x /usr/bin/*.py

FROM python:3.10.0-slim
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/bin /usr/bin

ARG OSC_S3_BUCKET=osclimatedata
ARG OSC_S3_HAZARD_PATH=hazard/hazard.zarr
ARG OSC_S3_SECRET_KEY
ARG OSC_S3_ACCESS_KEY

ENV OSC_S3_BUCKET=${OSC_S3_BUCKET}
ENV OSC_S3_HAZARD_PATH=${OSC_S3_HAZARD_PATH}
ENV OSC_S3_SECRET_KEY=${OSC_S3_SECRET_KEY}
ENV OSC_S3_ACCESS_KEY=${OSC_S3_ACCESS_KEY}