#!/bin/sh

set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
env_file="$repo_dir/.env"
example_file="$repo_dir/.env.example"
managed_marker_name=".mainstay-local-managed-data-root"
changes_started=false

abort_install() {
    if [ "$changes_started" = true ]; then
        printf '\n%s\n' \
            'Installation interrupted after configuration began. Review .env and the selected data root before retrying.' >&2
        exit 130
    fi
    printf '\n%s\n' 'Installation aborted. No changes were made.' >&2
    exit 130
}

trap abort_install HUP INT TERM

if [ ! -f "$example_file" ]; then
    printf '%s\n' "Missing environment template: $example_file" >&2
    exit 1
fi

source_file=$example_file
env_existed=false
if [ -f "$env_file" ]; then
    source_file=$env_file
    env_existed=true
fi

env_default() {
    key=$1
    fallback=$2
    awk -v key="$key" -v fallback="$fallback" '
        BEGIN { found = 0; value = "" }
        index($0, key "=") == 1 {
            value = substr($0, length(key) + 2)
            found = 1
        }
        END { print found ? value : fallback }
    ' "$source_file"
}

prompt_value() {
    label=$1
    default_value=$2
    if [ -n "$default_value" ]; then
        printf '%s [%s]: ' "$label" "$default_value" >&2
    else
        printf '%s [Docker-managed volumes]: ' "$label" >&2
    fi
    if ! IFS= read -r response; then
        abort_install
    fi
    case $(printf '%s' "$response" | tr '[:upper:]' '[:lower:]') in
        abort|quit|q) abort_install ;;
    esac
    if [ -z "$response" ]; then
        response=$default_value
    fi
    printf '%s\n' "$response"
}

prompt_yes_no() {
    label=$1
    default_value=$2
    while :; do
        answer=$(prompt_value "$label" "$default_value")
        case $(printf '%s' "$answer" | tr '[:upper:]' '[:lower:]') in
            y|yes) printf '%s\n' yes; return ;;
            n|no) printf '%s\n' no; return ;;
            *) printf '%s\n' 'Please enter yes, no, or abort.' >&2 ;;
        esac
    done
}

valid_port() {
    awk -v port="$1" 'BEGIN {
        exit !(port ~ /^[0-9]+$/ && port + 0 >= 1 && port + 0 <= 65535)
    }'
}

prompt_port() {
    label=$1
    default_value=$2
    while :; do
        port=$(prompt_value "$label" "$default_value")
        if valid_port "$port"; then
            printf '%s\n' "$port"
            return
        fi
        printf '%s\n' 'Enter a port from 1 through 65535, or abort.' >&2
    done
}

prompt_bind_address() {
    label=$1
    default_value=$2
    while :; do
        address=$(prompt_value "$label" "$default_value")
        case "$address" in
            ''|*[!A-Za-z0-9._-]*)
                printf '%s\n' \
                    'Enter an IPv4 address or hostname without spaces, or abort.' >&2
                ;;
            *) printf '%s\n' "$address"; return ;;
        esac
    done
}

set_env_value() {
    key=$1
    value=$2
    temp_file=$(mktemp "$repo_dir/.env.install.XXXXXX")
    awk -v key="$key" -v value="$value" '
        BEGIN { found = 0 }
        index($0, key "=") == 1 {
            if (!found) {
                print key "=" value
                found = 1
            }
            next
        }
        { print }
        END {
            if (!found) print key "=" value
        }
    ' "$env_file" > "$temp_file"
    chmod 600 "$temp_file"
    mv "$temp_file" "$env_file"
}

printf '%s\n' 'Mainstay first-install wizard'
printf '%s\n' \
    'IMPORTANT: Run each Mainstay instance from its own dedicated deployment directory.'
printf '%s\n' \
    'Do not share this checkout, its .env, or its Compose lifecycle between instances.'
printf '%s\n' \
    'Press Enter to accept each displayed default. Enter abort, quit, or q at any prompt to stop.'
if [ "$env_existed" = true ]; then
    printf '%s\n' \
        'An existing .env was found; its configured values are shown as defaults.'
else
    printf '%s\n' \
        'No .env was found; shipped defaults are shown and new secrets will be generated only after confirmation.'
fi
printf '\n'

configured_data_root=$(env_default MAINSTAY_DATA_ROOT "")
if [ "$env_existed" = false ] && [ -z "$configured_data_root" ]; then
    configured_data_root="$repo_dir/.mainstay-data"
fi
data_root=$(prompt_value 'Dedicated data root' "$configured_data_root")
case "$data_root" in
    '~') data_root=$HOME ;;
    '~/'*) data_root="$HOME/${data_root#\~/}" ;;
esac
if [ -n "$data_root" ]; then
    case "$data_root" in
        /*) ;;
        *)
            printf '%s\n' \
                'The data root must be an absolute path, or blank for Docker-managed volumes.' >&2
            exit 2
            ;;
    esac
    case "$data_root" in
        /|"$HOME"|"$repo_dir")
            printf '%s\n' \
                'Choose a dedicated subdirectory; the filesystem root, home directory, and repository cannot be data roots.' >&2
            exit 2
            ;;
        *:*)
            printf '%s\n' 'The data root must not contain a colon.' >&2
            exit 2
            ;;
    esac
fi

dashboard_bind=$(prompt_bind_address \
    'Dashboard bind address' \
    "$(env_default MAINSTAY_LOCAL_BIND_ADDRESS 0.0.0.0)")
dashboard_port=$(prompt_port \
    'Dashboard host port' \
    "$(env_default MAINSTAY_LOCAL_PORT 8788)")
safebox_bind=$(prompt_bind_address \
    'Safebox Web bind address' \
    "$(env_default MAINSTAY_SAFEBOX_BIND_ADDRESS 0.0.0.0)")
safebox_port=$(prompt_port \
    'Safebox Web host port' \
    "$(env_default MAINSTAY_SAFEBOX_PORT 8888)")

if [ "$dashboard_bind" = "$safebox_bind" ] && \
    [ "$dashboard_port" = "$safebox_port" ]; then
    printf '%s\n' \
        'Dashboard and Safebox Web cannot use the same host address and port.' >&2
    exit 2
fi

start_after=$(prompt_yes_no 'Start Mainstay after configuration? (yes/no)' yes)

managed_data_root=false
if [ -n "$data_root" ]; then
    marker="$data_root/$managed_marker_name"
    if [ -f "$marker" ] && \
        grep -qx 'org.mainstay.local-managed-data-root:v1' "$marker"; then
        managed_data_root=true
    elif [ ! -e "$data_root" ] || \
        { [ -d "$data_root" ] && \
          [ -z "$(find "$data_root" -mindepth 1 -print -quit)" ]; }; then
        managed_data_root=true
    elif [ "$env_existed" = false ]; then
        printf '%s\n' \
            "Refusing to adopt the non-empty unmarked data root: $data_root" >&2
        printf '%s\n' \
            'Choose a new dedicated directory so teardown cannot remove unrelated files.' >&2
        exit 1
    fi
fi

printf '\n%s\n' 'Review'
printf '  Data root:       %s\n' "${data_root:-Docker-managed named volumes}"
printf '  Dashboard:       %s:%s\n' "$dashboard_bind" "$dashboard_port"
printf '  Safebox Web:     %s:%s\n' "$safebox_bind" "$safebox_port"
printf '  Start afterward: %s\n' "$start_after"
if [ -n "$data_root" ] && [ "$managed_data_root" = false ]; then
    printf '%s\n' \
        '  Teardown:        existing unmarked data root will be preserved'
else
    printf '%s\n' \
        '  Teardown:        containers, volumes, configuration, and managed data can be removed'
fi
printf '\n'

proceed=$(prompt_yes_no 'Write this configuration? (yes/no)' no)
if [ "$proceed" != yes ]; then
    abort_install
fi

changes_started=true
if [ -n "$data_root" ]; then
    "$repo_dir/init-env.sh" --data-root "$data_root"
else
    "$repo_dir/init-env.sh"
fi

set_env_value MAINSTAY_LOCAL_BIND_ADDRESS "$dashboard_bind"
set_env_value MAINSTAY_LOCAL_PORT "$dashboard_port"
set_env_value MAINSTAY_SAFEBOX_BIND_ADDRESS "$safebox_bind"
set_env_value MAINSTAY_SAFEBOX_PORT "$safebox_port"

if [ -n "$data_root" ] && [ "$managed_data_root" = true ]; then
    marker="$data_root/$managed_marker_name"
    printf '%s\n' 'org.mainstay.local-managed-data-root:v1' > "$marker"
    chmod 600 "$marker"
fi

printf '%s\n' 'Mainstay configuration is ready in .env.'
if [ "$start_after" = yes ]; then
    "$repo_dir/start-mainstay.sh"
else
    printf '%s\n' 'Run ./start-mainstay.sh when you are ready.'
fi
