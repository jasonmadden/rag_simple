FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Optional system deps for compiling or debugging
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash build-essential curl vim && \
    rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /app/.venv

RUN chmod -R 755 /app/.venv

# Upgrade pip in venv
RUN . /app/.venv/bin/activate && pip install --upgrade pip

# Make sure venv is always on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Default: stay in an interactive shell with venv active
CMD ["/bin/bash", "-lc", "source /app/.venv/bin/activate && exec bash"]
