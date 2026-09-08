#!/bin/sh

set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
env_file="$repo_dir/.env"
compose_file="$repo_dir/docker-compose.yaml"
worker=service-acorn-worker
worker_was_running=false

if [ ! -f "$env_file" ]; then
    printf '%s\n' 'Cannot check the reserve because .env is missing.' >&2
    exit 1
fi
if ! command -v docker >/dev/null 2>&1; then
    printf '%s\n' 'Docker is required to check the service-Acorn reserve.' >&2
    exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
    printf '%s\n' 'The Docker Compose plugin is required.' >&2
    exit 1
fi

compose() {
    docker compose \
        --env-file "$env_file" \
        --project-directory "$repo_dir" \
        -f "$compose_file" \
        "$@"
}

restore_worker() {
    status=$?
    trap - EXIT HUP INT TERM
    if [ "$worker_was_running" = true ]; then
        if ! compose up -d --no-deps "$worker"; then
            printf '%s\n' \
                'The reserve check completed, but the service-Acorn worker could not be restarted.' >&2
            status=1
        fi
    fi
    exit "$status"
}
trap restore_worker EXIT HUP INT TERM

if [ -n "$(compose ps --status running --quiet "$worker")" ]; then
    worker_was_running=true
    compose stop "$worker"
fi

compose run --rm --no-deps "$worker" \
    python -m app.service_acorn_worker balance
