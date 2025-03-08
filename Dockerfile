FROM ubuntu:22.04

# Add the UV binary to the image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables to avoid interaction during installation
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
apt-get install -y --no-install-recommends \
ca-certificates \
curl \
build-essential \
git \
python3 \
pkg-config \
python3-icu \
libicu-dev && \
rm -rf /var/lib/apt/lists/*

RUN df -h
RUN uname
RUN uname -m 

RUN useradd -m -s /bin/bash user
USER user

WORKDIR /app


RUN uv python install 3.12
RUN uv python pin 3.12

COPY --chown=user ./data /app/data
COPY --chown=user ./scripts /app/scripts
COPY --chown=user ./src /app/src
COPY --chown=user ./static /app/static
COPY --chown=user ./templates /app/templates
COPY --chown=user ./pyproject.toml /app/pyproject.toml

RUN bash scripts/0_setup_cpu.sh
RUN bash scripts/1_prep.sh
# CMD [".venv/bin/python", "src/run_demo.py"]
# CMD ["/bin/bash"]