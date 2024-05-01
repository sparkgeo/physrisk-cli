FROM python:3.10.0-slim-buster
LABEL authors="Sparkgeo UK"

RUN apt-get update && apt-get install -y \
    build-essential \
    libproj-dev \
    proj-data \
    proj-bin \
    python3-scipy

ADD requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

ADD app/get_asset_impact.py /usr/bin/get_asset_impact.py
RUN chmod +x /usr/bin/get_asset_impact.py

ARG OSC_S3_BUCKET=osclimatedata
ARG OSC_S3_HAZARD_PATH=hazard/hazard.zarr
ARG OSC_S3_SECRET_KEY
ARG OSC_S3_ACCESS_KEY

ENV OSC_S3_BUCKET=${OSC_S3_BUCKET}
ENV OSC_S3_HAZARD_PATH=${OSC_S3_HAZARD_PATH}
ENV OSC_S3_SECRET_KEY=${OSC_S3_SECRET_KEY}
ENV OSC_S3_ACCESS_KEY=${OSC_S3_ACCESS_KEY}