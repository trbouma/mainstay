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
    selected_port=$2
    original_port=$3
    if [ "$env_existed" = true ] && [ "$selected_port" = "$original_port" ]; then
        return
    fi
    if port_is_listening "$selected_port"; then
        printf '%s\n' "$label port $selected_port is already in use." >&2
        exit 1
    else
        result=$?
        if [ "$result" -eq 2 ]; then
            printf '%s\n' \
                'ADVISORY: Neither ss nor lsof is available; host port occupancy could not be checked.' >&2
        fi
    fi
}

check_data_root_writable() {
    selected_root=$1
    if [ -z "$selected_root" ]; then
        return
    fi
    if [ -e "$selected_root" ]; then
        if [ ! -d "$selected_root" ]; then
            printf '%s\n' "The selected data root is not a directory: $selected_root" >&2
            exit 1
        fi
        if [ ! -w "$selected_root" ] || [ ! -x "$selected_root" ]; then
            printf '%s\n' "The selected data root is not writable: $selected_root" >&2
            exit 1
        fi
        return
    fi

    writable_parent=$selected_root
    while [ ! -e "$writable_parent" ]; do
        next_parent=$(dirname -- "$writable_parent")
        if [ "$next_parent" = "$writable_parent" ]; then
            break
        fi
        writable_parent=$next_parent
    done
    if [ ! -d "$writable_parent" ] || [ ! -w "$writable_parent" ] || \
        [ ! -x "$writable_parent" ]; then
        printf '%s\n' \
            "The installer cannot create the data root beneath: $writable_parent" >&2
        exit 1
    fi
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

prompt_https_url() {
    label=$1
    default_value=$2
    while :; do
        url=$(prompt_value "$label" "$default_value")
        case "$url" in
            https://?*)
                case "$url" in
                    *[[:space:]]*|*'?'*|*'#'*) ;;
                    *)
                        authority=${url#https://}
                        authority=${authority%%/*}
                        case "$authority" in
                            ''|*@*) ;;
                            *) printf '%s\n' "$url"; return ;;
                        esac
                        ;;
                esac
                ;;
        esac
        printf '%s\n' \
            'Enter an external https:// mint URL without credentials, a query, fragment, or spaces; or abort.' >&2
    done
}

prompt_external_relay() {
    label=$1
    default_value=$2
    while :; do
        relay=$(prompt_value "$label" "$default_value")
        case $(printf '%s' "$relay" | tr '[:upper:]' '[:lower:]') in
            none) printf '%s\n' ""; return ;;
        esac
        case "$relay" in
            wss://?*)
                case "$relay" in
                    *[[:space:]]*|*'#'*) ;;
                    *)
                        authority=${relay#wss://}
                        authority=${authority%%/*}
                        case "$authority" in
                            ''|*@*|*,*) ;;
                            *) printf '%s\n' "$relay"; return ;;
                        esac
                        ;;
                esac
                ;;
        esac
        printf '%s\n' \
            'Enter one external wss:// relay URL, none, or abort.' >&2
    done
}

prompt_project_name() {
    default_value=$1
    while :; do
        project_name=$(prompt_value 'Compose project name' "$default_value")
        case "$project_name" in
            [a-z0-9]*)
                case "$project_name" in
                    *[!a-z0-9_-]*) ;;
                    *) printf '%s\n' "$project_name"; return ;;
                esac
                ;;
        esac
        printf '%s\n' \
            'Use a unique lowercase name containing only letters, numbers, hyphens, or underscores.' >&2
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

print_fee_reserve_advisory() {
    printf '%s\n' \
        'ADVISORY: Lightning-address delivery requires an operator-funded service-Acorn fee reserve.'
    printf '%s\n' \
        'Mainstay does not transfer funds automatically. After first startup, fund at least 100 sats while the worker is stopped:'
    printf '%s\n' \
        '  docker compose stop service-acorn-worker'
    printf '%s\n' \
        '  docker compose run --rm --no-deps service-acorn-worker python -m app.service_acorn_worker fund 100'
    printf '%s\n' \
        '  docker compose up -d service-acorn-worker'
    printf '%s\n' \
        'The funding command reports the resulting balance. Check it later with: ./reserve-balance.sh'
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

compose_project_default=$(env_default COMPOSE_PROJECT_NAME mainstay-local)
compose_project_name=$(prompt_project_name "$compose_project_default")
configured_data_root=$(env_default MAINSTAY_DATA_ROOT "")
configured_data_parent=$(env_default MAINSTAY_DATA_PARENT "")
configured_data_directory_name=$(env_default MAINSTAY_DATA_DIRECTORY_NAME "")
legacy_data_layout=false
if [ "$env_existed" = true ] && [ -n "$configured_data_root" ] && \
    [ -z "$configured_data_parent" ]; then
    legacy_data_layout=true
    data_root=$(prompt_value \
        'Existing dedicated instance data root' "$configured_data_root")
    data_parent=$(dirname -- "$data_root")
else
    if [ "$env_existed" = false ] && [ -z "$configured_data_parent" ]; then
        configured_data_parent="$repo_dir/.mainstay-data"
    fi
    data_parent=$(prompt_value 'Data parent directory' "$configured_data_parent")
    case "$data_parent" in
        '~') data_parent=$HOME ;;
        '~/'*) data_parent="$HOME/${data_parent#\~/}" ;;
    esac
    data_directory_name=$configured_data_directory_name
    if [ -z "$data_directory_name" ]; then
        if [ "$env_existed" = true ] && [ -n "$configured_data_root" ]; then
            data_directory_name=$(basename -- "$configured_data_root")
        else
            data_directory_name=$compose_project_name
        fi
    fi
    if [ -n "$data_parent" ]; then
        data_root="$data_parent/$data_directory_name"
    else
        data_root=""
    fi
fi
if [ "$legacy_data_layout" = true ]; then
    data_directory_name=$(basename -- "$data_root")
fi
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
if [ "$env_existed" = true ] && \
    [ "$data_root" != "$configured_data_root" ]; then
    printf '%s\n' \
        "Refusing to change MAINSTAY_DATA_ROOT from ${configured_data_root:-Docker-managed volumes}." >&2
    printf '%s\n' \
        'Move existing data with an explicit stopped-service migration instead.' >&2
    exit 1
fi

dashboard_bind_default=$(env_default MAINSTAY_LOCAL_BIND_ADDRESS 0.0.0.0)
dashboard_port_default=$(env_default MAINSTAY_LOCAL_PORT 8788)
safebox_bind_default=$(env_default MAINSTAY_SAFEBOX_BIND_ADDRESS 0.0.0.0)
safebox_port_default=$(env_default MAINSTAY_SAFEBOX_PORT 8888)
lightning_mint_default=$(env_default \
    MAINSTAY_LIGHTNING_MINT_URL https://mint.safebox.dev)
external_relay_default=$(env_default \
    SAFEBOX_NIP05_EXTERNAL_RELAYS wss://spurline.safebox.dev)
dashboard_bind=$(prompt_bind_address \
    'Dashboard bind address' "$dashboard_bind_default")
dashboard_port=$(prompt_port \
    'Dashboard host port' "$dashboard_port_default")
safebox_bind=$(prompt_bind_address \
    'Safebox Web bind address' "$safebox_bind_default")
safebox_port=$(prompt_port \
    'Safebox Web host port' "$safebox_port_default")
lightning_mint_url=$(prompt_https_url \
    'External Lightning mint URL' "$lightning_mint_default")
external_relay=$(prompt_external_relay \
    'External inbox relay URL (or none)' "$external_relay_default")

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

printf '\n%s\n' 'Running read-only preflight checks...'
if ! command -v docker >/dev/null 2>&1; then
    printf '%s\n' 'Docker is required to install Mainstay.' >&2
    exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
    printf '%s\n' 'The Docker Compose plugin is required to install Mainstay.' >&2
    exit 1
fi
if ! docker info >/dev/null 2>&1; then
    printf '%s\n' 'Start Docker before installing Mainstay.' >&2
    exit 1
fi
if ! command -v openssl >/dev/null 2>&1; then
    printf '%s\n' 'OpenSSL is required to generate Mainstay secrets.' >&2
    exit 1
fi
if [ "$env_existed" = false ]; then
    existing_project_containers=$(docker ps -q \
        --filter "label=com.docker.compose.project=$compose_project_name")
    if [ -n "$existing_project_containers" ]; then
        printf '%s\n' \
            "Compose project '$compose_project_name' already has containers on this host." >&2
        printf '%s\n' \
            'Choose a unique project name so this deployment cannot manage another instance.' >&2
        exit 1
    fi
fi
check_data_root_writable "$data_root"
check_available_port Dashboard "$dashboard_port" "$dashboard_port_default"
check_available_port 'Safebox Web' "$safebox_port" "$safebox_port_default"
printf '%s\n' 'Preflight checks passed. No configuration has been written.'

printf '\n%s\n' 'Review'
printf '  Compose project: %s\n' "$compose_project_name"
if [ "$legacy_data_layout" = false ]; then
    printf '  Data parent:     %s\n' "${data_parent:-Docker-managed named volumes}"
fi
printf '  Data root:       %s\n' "${data_root:-Docker-managed named volumes}"
printf '  Dashboard:       %s:%s\n' "$dashboard_bind" "$dashboard_port"
printf '  Safebox Web:     %s:%s\n' "$safebox_bind" "$safebox_port"
printf '  Lightning mint:  %s\n' "$lightning_mint_url"
printf '  External relay:  %s\n' "${external_relay:-not advertised}"
printf '%s\n' \
    '  Required action: fund at least 100 sats of service-Acorn fee reserve after startup'
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
set_env_value MAINSTAY_LIGHTNING_MINT_URL "$lightning_mint_url"
set_env_value SAFEBOX_NIP05_EXTERNAL_RELAYS "$external_relay"
set_env_value COMPOSE_PROJECT_NAME "$compose_project_name"
set_env_value MAINSTAY_DATA_PARENT "$data_parent"
set_env_value MAINSTAY_DATA_DIRECTORY_NAME "$data_directory_name"

if [ -n "$data_root" ] && [ "$managed_data_root" = true ]; then
    marker="$data_root/$managed_marker_name"
    printf '%s\n' 'org.mainstay.local-managed-data-root:v1' > "$marker"
    chmod 600 "$marker"
fi

"$repo_dir/save-recovery-env.sh"

printf '%s\n' 'Mainstay configuration is ready in .env.'
printf '\n'
print_fee_reserve_advisory
if [ "$start_after" = yes ]; then
    "$repo_dir/start-mainstay.sh"
else
    printf '%s\n' 'Run ./start-mainstay.sh when you are ready.'
fi
