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