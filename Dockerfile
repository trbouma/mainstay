# syntax=docker/dockerfile:1

FROM python:3.11-slim-bookworm AS builder

ARG POETRY_VERSION=1.8.2

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1

RUN python -m pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./
COPY app /app/app
RUN poetry install --only main --no-ansi


FROM python:3.11-slim-bookworm AS runtime

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MAINSTAY_LOCAL_HOST=0.0.0.0 \
    MAINSTAY_LOCAL_PORT=8788 \
    MAINSTAY_LOCAL_CONFIG=/app/data/mainstay-local.json

RUN groupadd --gid 10001 mainstay \
    && useradd --uid 10001 --gid mainstay --create-home --shell /usr/sbin/nologin mainstay \
    && install -d -o mainstay -g mainstay /app/data

WORKDIR /app

COPY --from=builder --chown=mainstay:mainstay /app/.venv /app/.venv
COPY --from=builder --chown=mainstay:mainstay /app/app /app/app

USER mainstay

EXPOSE 8788
VOLUME ["/app/data"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import json, urllib.request; response = json.load(urllib.request.urlopen('http://127.0.0.1:8788/health', timeout=3)); assert response.get('status') == 'ok'"]

CMD ["mainstay-local", "serve", "--config", "/app/data/mainstay-local.json", "--host", "0.0.0.0", "--port", "8788"]
