#!/bin/sh

set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
env_file="$repo_dir/.env"
managed_marker_name=".mainstay-local-managed-data-root"

abort_teardown() {
    printf '\n%s\n' 'Teardown aborted. No data was removed.' >&2
    exit 0
}

trap abort_teardown HUP INT TERM

if [ ! -f "$env_file" ]; then
    printf '%s\n' 'No .env was found. There is no installer-managed instance to tear down.' >&2
    exit 1
fi

read_value() {
    awk -v key="$1" '
        index($0, key "=") == 1 {
            value = substr($0, length(key) + 2)
        }
        END { print value }
    ' "$env_file"
}

data_root=$(read_value MAINSTAY_DATA_ROOT)
managed_data_root=false
if [ -n "$data_root" ]; then
    marker="$data_root/$managed_marker_name"
    case "$data_root" in
        /|"$HOME"|"$repo_dir") ;;
        *)
            if [ -f "$marker" ] && \
                grep -qx 'org.mainstay.local-managed-data-root:v1' "$marker"; then
                managed_data_root=true
            fi
            ;;
    esac
fi

printf '%s\n' 'Mainstay destructive teardown'
printf '%s\n' \
    'IMPORTANT: This command acts on the Mainstay instance owned by this deployment directory.'
printf '%s\n' \
    'This stops the Compose project and removes its containers, network, and Docker-managed volumes.'
if [ -z "$data_root" ]; then
    printf '%s\n' 'Persistent data uses Docker-managed named volumes; those volumes will be removed.'
elif [ "$managed_data_root" = true ]; then
    printf '%s\n' "The installer-managed data root will be deleted: $data_root"
else
    printf '%s\n' "The unmarked data root will be preserved: $data_root"
fi
printf '%s\n' \
    'The .env file and generated installation-identity state will also be deleted. Built images are retained.'
printf '%s\n' \
    'Enter DELETE to continue, or enter abort, quit, q, or anything else to stop.'
printf '> '
if ! IFS= read -r confirmation; then
    abort_teardown
fi
if [ "$confirmation" != DELETE ]; then
    abort_teardown
fi

if ! command -v docker >/dev/null 2>&1; then
    printf '%s\n' \
        'Docker is required to prove that the instance has stopped before deleting its data.' >&2
    exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
    printf '%s\n' 'The Docker Compose plugin is required for teardown.' >&2
    exit 1
fi

docker compose down --volumes --remove-orphans

if [ "$managed_data_root" = true ]; then
    rm -rf -- "$data_root"
fi
rm -rf -- "$repo_dir/build/mainstay-local"
rm -f -- "$env_file"

printf '%s\n' 'Mainstay containers, managed data, and generated configuration were removed.'
if [ -n "$data_root" ] && [ "$managed_data_root" = false ]; then
    printf '%s\n' \
        'The data root was not installer-managed and remains in place.'
fi
