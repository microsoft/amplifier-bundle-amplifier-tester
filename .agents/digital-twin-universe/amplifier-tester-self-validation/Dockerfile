ARG PYTHON_IMAGE
FROM ${PYTHON_IMAGE}
# No source, settings, credentials or Docker socket is copied into this image.
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN useradd --uid 1000 --create-home tester
USER tester
WORKDIR /home/tester
RUN /usr/local/bin/python -m venv /home/tester/venv \
    && mkdir -p /home/tester/evidence
