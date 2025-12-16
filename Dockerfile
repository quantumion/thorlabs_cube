FROM python:3.12-slim-bookworm
SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_ROOT_USER_ACTION=ignore
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install base tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY . .

RUN python -m pip install --no-cache-dir .

ENTRYPOINT ["aqctl_thorlabs_cube"]
CMD ["-p", "3255", "-P", "kpz101", "-d", "/dev/ttyUSB0", "--bind", "*"]
