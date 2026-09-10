# r360-integration gate image.
#
# A test driver, nothing more. This repository owns no production logic, so this image
# carries only what is needed to compose the stack and observe it: the contract bindings,
# an MQTT client, a gRPC client, and a database driver.
FROM debian:bookworm-slim@sha256:88200866dfff7ea7f5cbcb6ec7c8a701889efe6fe859fe64d6990e4b07ea4171

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3=3.11.2-1+b1 \
      python3-venv=3.11.2-1+b1 \
      make \
      git \
      ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt
ENV PATH="/opt/venv/bin:${PATH}"
ENV PYTHONDONTWRITEBYTECODE=1

RUN git config --global --add safe.directory '*'

WORKDIR /work
