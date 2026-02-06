FROM python:3.14.3-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project metadata first for efficient rebuilds
COPY pyproject.toml /app/
COPY requirements.txt /app/

# Install Python deps
RUN python -m pip install --upgrade pip setuptools wheel
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Copy source and tests
COPY src/ /app/src/
COPY tests/ /app/tests/
COPY .specify/ /app/.specify/

ENV PATH="/app/src:${PATH}"

CMD ["pytest", "-q"]
