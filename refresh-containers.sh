#!/bin/sh

set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$repo_dir"

printf '%s\n' 'Pulling the latest changes...'
git pull

"$repo_dir/init-env.sh"

printf '%s\n' 'Building the Mainstay Local service images...'
docker compose build

printf '%s\n' 'Recreating the Mainstay Local service bundle...'
docker compose up --force-recreate --detach

printf '%s\n' 'Mainstay Local service bundle refreshed.'
docker compose ps

printf '%s\n' 'Waiting for the managed service status check...'
attempt=1
max_attempts=30
while ! docker compose exec -T mainstay-local python -c \
    "import json, urllib.request; response = json.load(urllib.request.urlopen('http://127.0.0.1:8788/status', timeout=3)); assert response.get('status') == 'ok'" \
    >/dev/null 2>&1
do
    if [ "$attempt" -ge "$max_attempts" ]; then
        printf '%s\n' 'Managed service status check failed after 60 seconds.' >&2
        docker compose ps >&2
        exit 1
    fi
    attempt=$((attempt + 1))
    sleep 2
done

printf '%s\n' 'Managed service status check passed: status=ok'

printf '%s\n' 'Waiting for the service Acorn worker to initialize...'
attempt=1
while :
do
    worker_id=$(docker compose ps -q service-acorn-worker)
    worker_health=$(
        docker inspect --format '{{.State.Health.Status}}' "$worker_id" \
            2>/dev/null || true
    )
    if [ "$worker_health" = "healthy" ]; then
        break
    fi
    if [ "$attempt" -ge "$max_attempts" ]; then
        printf '%s\n' \
            'Service Acorn worker did not initialize within 60 seconds.' >&2
        docker compose ps >&2
        docker compose logs --tail 50 service-acorn-worker >&2
        exit 1
    fi
    attempt=$((attempt + 1))
    sleep 2
done

printf '%s\n' 'Service Acorn worker initialized and healthy.'
