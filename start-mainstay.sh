#!/bin/sh

set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$repo_dir"

data_root=
force_recreate=false
build=true

usage() {
    printf '%s\n' \
        'Usage: ./start-mainstay.sh [--data-root PATH] [--no-build] [--force-recreate]'
}

env_value() {
    key=$1
    fallback=$2
    awk -v key="$key" -v fallback="$fallback" '
        index($0, key "=") == 1 {
            print substr($0, length(key) + 2)
            found = 1
            exit
        }
        END { if (!found) print fallback }
    ' .env
}

port_is_listening() {
    checked_port=$1
    if command -v ss >/dev/null 2>&1; then
        ss -H -ltn 2>/dev/null | awk -v port="$checked_port" '
            $4 ~ (":" port "$") { found = 1 }
            END { exit !found }
        '
        return
    fi
    if command -v lsof >/dev/null 2>&1; then
        lsof -nP -iTCP:"$checked_port" -sTCP:LISTEN >/dev/null 2>&1
        return
    fi
    return 2
}

check_available_port() {
    label=$1
    env_key=$2
    expected_service=$3
    selected_port=$4
    owner_rows=$(docker ps \
        --filter "publish=$selected_port" \
        --format '{{.Names}}|{{.Label "com.docker.compose.project"}}|{{.Label "com.docker.compose.service"}}' \
        2>/dev/null || true)
    if [ -n "$owner_rows" ]; then
        foreign_rows=$(printf '%s\n' "$owner_rows" | awk \
            -F'|' -v project="$compose_project_name" \
            -v service="$expected_service" \
            '$2 != project || $3 != service { print }')
        if [ -z "$foreign_rows" ]; then
            return
        fi
        printf '%s\n' \
            "$label host port $selected_port is already published by:" >&2
        printf '%s\n' "$foreign_rows" | awk -F'|' '
            { printf "  %s%s\n", $1, ($2 == "" ? "" : " (project " $2 ")") }
        ' >&2
        printf '%s\n' \
            "Set $env_key to an unused host port for project '$compose_project_name'." >&2
        exit 1
    fi
    if port_is_listening "$selected_port"; then
        printf '%s\n' "$label host port $selected_port is already in use." >&2
        printf '%s\n' \
            "Set $env_key to an unused host port for project '$compose_project_name'." >&2
        exit 1
    else
        result=$?
        if [ "$result" -eq 2 ]; then
            printf '%s\n' \
                'ADVISORY: Neither ss nor lsof is available; host port occupancy could not be checked.' >&2
        fi
    fi
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --data-root)
            if [ "$#" -lt 2 ] || [ -z "$2" ]; then
                printf '%s\n' '--data-root requires a path.' >&2
                usage >&2
                exit 2
            fi
            data_root=$2
            shift 2
            ;;
        --no-build)
            build=false
            shift
            ;;
        --force-recreate)
            force_recreate=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            printf '%s\n' "Unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if ! command -v docker >/dev/null 2>&1; then
    printf '%s\n' 'Docker with Compose is required to start Mainstay.' >&2
    exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
    printf '%s\n' 'The Docker Compose plugin is required to start Mainstay.' >&2
    exit 1
fi
if ! docker info >/dev/null 2>&1; then
    printf '%s\n' 'Start Docker before starting Mainstay.' >&2
    exit 1
fi

printf '%s\n' 'Preparing the Mainstay environment...'
if [ -n "$data_root" ]; then
    "$repo_dir/init-env.sh" --data-root "$data_root"
else
    "$repo_dir/init-env.sh"
fi
"$repo_dir/save-recovery-env.sh"

printf '%s\n' 'Validating the Mainstay Compose configuration...'
docker compose config --quiet

compose_project_name=${COMPOSE_PROJECT_NAME:-$(env_value COMPOSE_PROJECT_NAME mainstay-local)}
mainstay_port=${MAINSTAY_LOCAL_PORT:-$(env_value MAINSTAY_LOCAL_PORT 8788)}
safebox_port=${MAINSTAY_SAFEBOX_PORT:-$(env_value MAINSTAY_SAFEBOX_PORT 8888)}
printf '%s\n' 'Checking published host ports...'
check_available_port \
    Dashboard MAINSTAY_LOCAL_PORT mainstay-local "$mainstay_port"
check_available_port \
    'Safebox Web' MAINSTAY_SAFEBOX_PORT safebox-web "$safebox_port"

printf '%s\n' 'Starting the Mainstay service bundle...'
if [ "$build" = true ] && [ "$force_recreate" = true ]; then
    docker compose up --build --force-recreate --detach
elif [ "$build" = true ]; then
    docker compose up --build --detach
elif [ "$force_recreate" = true ]; then
    docker compose up --force-recreate --detach
else
    docker compose up --detach
fi

max_attempts=30
printf '%s\n' 'Waiting for the managed service status check...'
attempt=1
while ! docker compose exec -T mainstay-local python -c \
    "import json, urllib.request; response = json.load(urllib.request.urlopen('http://127.0.0.1:8788/status', timeout=3)); assert response.get('status') == 'ok'" \
    >/dev/null 2>&1
do
    if [ "$attempt" -ge "$max_attempts" ]; then
        printf '%s\n' 'Managed services did not become ready within 60 seconds.' >&2
        docker compose ps >&2
        docker compose logs --tail 50 mainstay-local clear grove spurline safebox-web >&2
        exit 1
    fi
    attempt=$((attempt + 1))
    sleep 2
done

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

printf '%s\n' 'Mainstay is ready.'
printf '%s\n' "Dashboard: http://127.0.0.1:${mainstay_port:-8788}/"
printf '%s\n' "Safebox Web: http://127.0.0.1:${safebox_port:-8888}/"
printf '%s\n' \
    'Operator milestones remain: commission services, verify and enable Clear treasury when required, fund the service Acorn, and configure production routes and TLS.'
