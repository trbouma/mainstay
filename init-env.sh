#!/bin/sh

set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
env_file="$repo_dir/.env"
example_file="$repo_dir/.env.example"
clear_volume="mainstay-local_clear-data"

if [ ! -f "$example_file" ]; then
    printf '%s\n' "Missing environment template: $example_file" >&2
    exit 1
fi

source_file="$env_file"
created=false
if [ ! -f "$env_file" ]; then
    source_file="$example_file"
    created=true
fi

read_value() {
    awk -v key="$1" '
        index($0, key "=") == 1 {
            value = substr($0, length(key) + 2)
        }
        END { print value }
    ' "$source_file"
}

master_secret=$(read_value CLEAR_MASTER_SECRET)
operator_token=$(read_value CLEAR_OPERATOR_TOKEN)

if [ -n "$master_secret" ] && [ -n "$operator_token" ]; then
    chmod 600 "$env_file"
    printf '%s\n' '.env already contains the required Clear secrets.'
    exit 0
fi

if ! command -v openssl >/dev/null 2>&1; then
    printf '%s\n' 'openssl is required to generate Clear secrets.' >&2
    exit 1
fi

if [ -z "$master_secret" ]; then
    if ! command -v docker >/dev/null 2>&1; then
        printf '%s\n' \
            'Docker is required to verify that no existing Clear volume is present.' >&2
        exit 1
    fi
    if ! docker info >/dev/null 2>&1; then
        printf '%s\n' \
            'Start Docker before generating a new Clear master secret.' >&2
        exit 1
    fi
    if docker volume inspect "$clear_volume" >/dev/null 2>&1; then
        printf '%s\n' \
            "Refusing to generate CLEAR_MASTER_SECRET because $clear_volume exists." >&2
        printf '%s\n' \
            'Recover the original .env or master secret associated with that mint.' >&2
        exit 1
    fi
    master_secret=$(openssl rand -hex 32)
fi

if [ -z "$operator_token" ]; then
    operator_token=$(openssl rand -hex 32)
fi

umask 077
temp_file=$(mktemp "$repo_dir/.env.tmp.XXXXXX")
cleanup() {
    rm -f -- "$temp_file"
}
trap cleanup EXIT HUP INT TERM

awk \
    -v master_secret="$master_secret" \
    -v operator_token="$operator_token" '
    BEGIN {
        found_master = 0
        found_operator = 0
    }
    /^CLEAR_MASTER_SECRET=/ {
        if (!found_master) {
            print "CLEAR_MASTER_SECRET=" master_secret
            found_master = 1
        }
        next
    }
    /^CLEAR_OPERATOR_TOKEN=/ {
        if (!found_operator) {
            print "CLEAR_OPERATOR_TOKEN=" operator_token
            found_operator = 1
        }
        next
    }
    { print }
    END {
        if (!found_master) {
            print "CLEAR_MASTER_SECRET=" master_secret
        }
        if (!found_operator) {
            print "CLEAR_OPERATOR_TOKEN=" operator_token
        }
    }
' "$source_file" >"$temp_file"

mv "$temp_file" "$env_file"
trap - EXIT HUP INT TERM
chmod 600 "$env_file"

if [ "$created" = true ]; then
    printf '%s\n' 'Created .env with generated Clear secrets.'
else
    printf '%s\n' 'Added missing Clear secrets to .env.'
fi
