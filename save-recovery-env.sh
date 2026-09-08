#!/bin/sh

set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
env_file="$repo_dir/.env"

if [ ! -f "$env_file" ]; then
    printf '%s\n' 'Cannot save recovery configuration because .env is missing.' >&2
    exit 1
fi

read_value() {
    file=$1
    key=$2
    awk -v key="$key" '
        index($0, key "=") == 1 {
            value = substr($0, length(key) + 2)
        }
        END { print value }
    ' "$file"
}

data_root=$(read_value "$env_file" MAINSTAY_DATA_ROOT)
if [ -z "$data_root" ]; then
    exit 0
fi
case "$data_root" in
    /*) ;;
    *)
        printf '%s\n' 'MAINSTAY_DATA_ROOT must be absolute.' >&2
        exit 1
        ;;
esac
if [ ! -d "$data_root" ]; then
    printf '%s\n' "Mainstay data root does not exist: $data_root" >&2
    exit 1
fi

recovery_file="$data_root/.env.recovery"
if [ -L "$recovery_file" ]; then
    printf '%s\n' 'Refusing to replace a symbolic-link recovery file.' >&2
    exit 1
fi

identity_keys='MAINSTAY_INSTALLATION_NSEC
CLEAR_MASTER_SECRET
CLEAR_MINT_SERVICE_NSEC
SPURLINE_SERVICE_NSEC
GROVE_SERVICE_NSEC
SAFEBOX_COOKIE_KEY'

for key in $identity_keys; do
    current_value=$(read_value "$env_file" "$key")
    if [ -z "$current_value" ]; then
        printf '%s\n' "Cannot save recovery configuration: $key is empty." >&2
        exit 1
    fi
    if [ -f "$recovery_file" ]; then
        recovery_value=$(read_value "$recovery_file" "$key")
        if [ -n "$recovery_value" ] && \
            [ "$recovery_value" != "$current_value" ]; then
            printf '%s\n' \
                "Refusing to overwrite .env.recovery: $key does not match." >&2
            printf '%s\n' \
                'Resolve the identity mismatch explicitly before updating recovery material.' >&2
            exit 1
        fi
    fi
done

umask 077
temp_file=$(mktemp "$data_root/.env.recovery.tmp.XXXXXX")
cleanup() {
    rm -f -- "$temp_file"
}
trap cleanup EXIT HUP INT TERM
cp "$env_file" "$temp_file"
chmod 600 "$temp_file"
mv "$temp_file" "$recovery_file"
trap - EXIT HUP INT TERM

printf '%s\n' "Saved recovery configuration: $recovery_file"

