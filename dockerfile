# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

# install build deps (gcc, libpq) in case some deps need compilation
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      gcc build-essential libpq-dev curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# create app user and working dir
RUN groupadd -r app && useradd -r -g app app
WORKDIR /app

# copy metadata first for better caching
COPY pyproject.toml uv.lock* ./

# upgrade pip
RUN python -m pip install --upgrade pip setuptools wheel

# install dependencies:
# If you produce a requirements.txt locally, it will be used.
# Otherwise pip will attempt to install the project via pyproject.toml build system.
RUN if [ -f "requirements.txt" ]; then \
      pip install --no-cache-dir -r requirements.txt; \
    else \
      pip install --no-cache-dir . ; \
    fi

# copy source code
COPY . /app

# create a non-root user to run the process
RUN chown -R app:app /app
USER app

# default command (use python to run your main script)
CMD ["python", "-u", "main.py"]
