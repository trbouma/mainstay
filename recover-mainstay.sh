#!/bin/sh

set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
env_file="$repo_dir/.env"
changes_started=false

abort_recovery() {
    if [ "$changes_started" = true ]; then
        printf '\n%s\n' \
            'Recovery interrupted after configuration began. The source data was not modified; inspect this deployment directory before retrying.' >&2
        exit 1
    fi
    printf '\n%s\n' 'Recovery aborted. No changes were made.' >&2
    exit 130
}

trap abort_recovery HUP INT TERM

if [ -f "$env_file" ]; then
    printf '%s\n' \
        'This deployment directory already contains .env; recovery will not overwrite it.' >&2
    printf '%s\n' \
        'Use a new dedicated deployment directory or remove it only after confirming it is not needed.' >&2
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

recovery_default() {
    key=$1
    fallback=$2
    value=$(read_value "$recovery_file" "$key")
    if [ -n "$value" ]; then
        printf '%s\n' "$value"
    else
        printf '%s\n' "$fallback"
    fi
}

recovery_image() {
    key=$1
    legacy_value=$2
    suffix=$3
    recovered_value=$(read_value "$recovery_file" "$key")
    case "$recovered_value" in
        ''|"$legacy_value")
            printf '%s-%s:local\n' "$compose_project_name" "$suffix"
            ;;
        *)
            printf '%s\n' "$recovered_value"
            ;;
    esac
}

prompt_value() {
    label=$1
    default_value=$2
    if [ -n "$default_value" ]; then
        printf '%s [%s]: ' "$label" "$default_value" >&2
    else
        printf '%s: ' "$label" >&2
    fi
    if ! IFS= read -r response; then
        abort_recovery
    fi
    case $(printf '%s' "$response" | tr '[:upper:]' '[:lower:]') in
        abort|quit|q) abort_recovery ;;
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

valid_project_name() {
    case "$1" in
        [a-z0-9]*)
            case "$1" in
                *[!a-z0-9_-]*) return 1 ;;
                *) return 0 ;;
            esac
            ;;
        *) return 1 ;;
    esac
}

prompt_project_name() {
    default_value=$1
    while :; do
        name=$(prompt_value 'New Compose project name' "$default_value")
        if valid_project_name "$name"; then
            printf '%s\n' "$name"
            return
        fi
        printf '%s\n' \
            'Use lowercase letters, numbers, hyphens, or underscores, beginning with a letter or number.' >&2
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
    port=$2
    if port_is_listening "$port"; then
        printf '%s\n' "$label port $port is already in use." >&2
        exit 1
    else
        result=$?
        if [ "$result" -eq 2 ]; then
            printf '%s\n' \
                'ADVISORY: Neither ss nor lsof is available; host port occupancy could not be checked.' >&2
        fi
    fi
}

printf '%s\n' 'Mainstay recovery wizard'
printf '%s\n' \
    'IMPORTANT: Recover into a new dedicated deployment directory.'
printf '%s\n' \
    'The prior container set must be stopped before another project attaches to this data.'
printf '%s\n' \
    'This script never generates replacement secrets and never renames the recovered data directory.'
printf '%s\n' \
    'Rename or move a filesystem or ZFS root before recovery, while every service is stopped.'
printf '%s\n' \
    'Enter abort, quit, or q at any prompt to stop without writing configuration.'
printf '\n'

data_root=$(prompt_value 'Existing instance data root' '')
case "$data_root" in
    '~') data_root=$HOME ;;
    '~/'*) data_root="$HOME/${data_root#\~/}" ;;
esac
case "$data_root" in
    /*) ;;
    *) printf '%s\n' 'The existing data root must be an absolute path.' >&2; exit 1 ;;
esac
if [ ! -d "$data_root" ] || [ ! -r "$data_root" ] || [ ! -w "$data_root" ]; then
    printf '%s\n' \
        "The existing data root must be a readable and writable directory: $data_root" >&2
    exit 1
fi

recovery_file="$data_root/.env.recovery"
if [ ! -f "$recovery_file" ] || [ -L "$recovery_file" ]; then
    printf '%s\n' \
        "A regular recovery environment was not found at: $recovery_file" >&2
    exit 1
fi

control_data_source=""
if [ -d "$data_root/mainstay-control" ]; then
    control_data_source="$data_root/mainstay-control"
elif [ -d "$data_root/mainstay-local" ]; then
    control_data_source="$data_root/mainstay-local"
else
    printf '%s\n' \
        'The data root contains neither mainstay-control nor legacy mainstay-local state.' >&2
    exit 1
fi
for service_directory in safebox-web spurline grove clear; do
    if [ ! -d "$data_root/$service_directory" ]; then
        printf '%s\n' \
            "Missing recovered service directory: $data_root/$service_directory" >&2
        exit 1
    fi
done

required_keys='MAINSTAY_INSTALLATION_NSEC
CLEAR_MASTER_SECRET
CLEAR_OPERATOR_TOKEN
CLEAR_MINT_SERVICE_NSEC
SPURLINE_SERVICE_NSEC
GROVE_SERVICE_NSEC
SAFEBOX_WEB_SERVICE_NSEC
SAFEBOX_COOKIE_KEY
SAFEBOX_ONBOARD_INVITE_CODE'
for key in $required_keys; do
    if [ -z "$(read_value "$recovery_file" "$key")" ]; then
        printf '%s\n' "Recovery configuration is missing required $key." >&2
        exit 1
    fi
done

data_directory_name=$(basename -- "$data_root")
recovered_project_name=$(read_value "$recovery_file" COMPOSE_PROJECT_NAME)
if [ -z "$recovered_project_name" ]; then
    recovered_project_name=mainstay-local
fi

printf '\n%s\n' 'Compose name and data-root name are separate during recovery.'
printf '  Existing data-root name: %s\n' "$data_directory_name"
printf '  Recovered Compose name:  %s\n' "$recovered_project_name"
printf '%s\n' 'Choose 1 to use the existing data-root name as the Compose name (recommended).'
printf '%s\n' 'Choose 2 to specify a different Compose name without renaming the data root.'
printf '%s\n' 'Enter abort to stop and rename the data root first.'
choice=$(prompt_value 'Choice (1/2)' 1)
case "$choice" in
    1)
        if ! valid_project_name "$data_directory_name"; then
            printf '%s\n' \
                'The data-root name is not a valid Compose project name; choose a different Compose name or rename the root first.' >&2
            exit 1
        fi
        compose_project_name=$data_directory_name
        ;;
    2)
        compose_project_name=$(prompt_project_name "$recovered_project_name")
        if [ "$compose_project_name" != "$data_directory_name" ]; then
            printf '%s\n' \
                'WARNING: The Compose project name will differ from the existing data-root name.' >&2
            printf '%s\n' \
                "The script will attach '$compose_project_name' to '$data_root' and will not rename that directory." >&2
            continue_mismatch=$(prompt_yes_no \
                'Continue with different names? (yes/no)' no)
            if [ "$continue_mismatch" != yes ]; then
                abort_recovery
            fi
        fi
        ;;
    *)
        printf '%s\n' 'Choose 1, 2, or abort.' >&2
        exit 1
        ;;
esac

mainstay_local_image=$(recovery_image \
    MAINSTAY_LOCAL_IMAGE mainstay-local:local control)
safebox_image=$(recovery_image SAFEBOX_IMAGE safebox-web:local safebox-web)
spurline_image=$(recovery_image \
    MAINSTAY_SPURLINE_IMAGE mainstay-local-spurline:local spurline)
grove_image=$(recovery_image \
    MAINSTAY_GROVE_IMAGE mainstay-local-grove:local grove)
clear_image=$(recovery_image \
    MAINSTAY_CLEAR_IMAGE mainstay-local-clear:local clear)

dashboard_bind=$(prompt_bind_address \
    'Dashboard bind address' \
    "$(recovery_default MAINSTAY_LOCAL_BIND_ADDRESS 0.0.0.0)")
dashboard_port=$(prompt_port \
    'Dashboard host port' \
    "$(recovery_default MAINSTAY_LOCAL_PORT 8788)")
safebox_bind=$(prompt_bind_address \
    'Safebox Web bind address' \
    "$(recovery_default MAINSTAY_SAFEBOX_BIND_ADDRESS 0.0.0.0)")
safebox_port=$(prompt_port \
    'Safebox Web host port' \
    "$(recovery_default MAINSTAY_SAFEBOX_PORT 8888)")
if [ "$dashboard_bind" = "$safebox_bind" ] && \
    [ "$dashboard_port" = "$safebox_port" ]; then
    printf '%s\n' \
        'Dashboard and Safebox Web cannot use the same host address and port.' >&2
    exit 1
fi
start_after=$(prompt_yes_no 'Start Mainstay after recovery? (yes/no)' yes)

printf '\n%s\n' 'Running read-only recovery preflight checks...'
if ! command -v docker >/dev/null 2>&1 || \
    ! docker compose version >/dev/null 2>&1 || \
    ! docker info >/dev/null 2>&1; then
    printf '%s\n' 'Docker with Compose must be running for recovery.' >&2
    exit 1
fi
selected_project_containers=$(docker ps -aq \
    --filter "label=com.docker.compose.project=$compose_project_name")
if [ -n "$selected_project_containers" ]; then
    printf '%s\n' \
        "Compose project '$compose_project_name' already has containers on this host." >&2
    printf '%s\n' 'Remove that project or choose another name before recovery.' >&2
    exit 1
fi
if [ "$recovered_project_name" != "$compose_project_name" ]; then
    old_project_running=$(docker ps -q \
        --filter "label=com.docker.compose.project=$recovered_project_name")
    if [ -n "$old_project_running" ]; then
        printf '%s\n' \
            "Recovered project '$recovered_project_name' still has running containers." >&2
        exit 1
    fi
fi
check_available_port Dashboard "$dashboard_port"
check_available_port 'Safebox Web' "$safebox_port"
docker compose --env-file "$recovery_file" config --quiet
printf '%s\n' 'Recovery preflight passed. No deployment configuration has been written.'

printf '\n%s\n' 'Recovery review'
printf '  Existing data root: %s\n' "$data_root"
printf '  Data-root name:     %s\n' "$data_directory_name"
printf '  Compose project:    %s\n' "$compose_project_name"
printf '  Image namespace:    %s-*\n' "$compose_project_name"
printf '  Control data:       %s\n' "$control_data_source"
printf '  Dashboard:          %s:%s\n' "$dashboard_bind" "$dashboard_port"
printf '  Safebox Web:        %s:%s\n' "$safebox_bind" "$safebox_port"
printf '  Start afterward:    %s\n' "$start_after"
if [ "$compose_project_name" != "$data_directory_name" ]; then
    printf '%s\n' \
        '  Advisory:          Compose and data-root names will remain different'
fi
printf '\n'
proceed=$(prompt_yes_no 'Attach this deployment to the recovered data? (yes/no)' no)
if [ "$proceed" != yes ]; then
    abort_recovery
fi

changes_started=true
data_parent=$(dirname -- "$data_root")
data_runtime_user="$(id -u):$(id -g)"
umask 077
temp_file=$(mktemp "$repo_dir/.env.recover.XXXXXX")
cleanup() {
    rm -f -- "$temp_file"
}
trap cleanup EXIT HUP INT TERM
awk \
    -v compose_project_name="$compose_project_name" \
    -v mainstay_local_image="$mainstay_local_image" \
    -v safebox_image="$safebox_image" \
    -v spurline_image="$spurline_image" \
    -v grove_image="$grove_image" \
    -v clear_image="$clear_image" \
    -v data_parent="$data_parent" \
    -v data_directory_name="$data_directory_name" \
    -v data_root="$data_root" \
    -v data_runtime_user="$data_runtime_user" \
    -v local_data_source="$control_data_source" \
    -v safebox_data_source="$data_root/safebox-web" \
    -v spurline_data_source="$data_root/spurline" \
    -v grove_data_source="$data_root/grove" \
    -v clear_data_source="$data_root/clear" \
    -v dashboard_bind="$dashboard_bind" \
    -v dashboard_port="$dashboard_port" \
    -v safebox_bind="$safebox_bind" \
    -v safebox_port="$safebox_port" '
    BEGIN {
        values["COMPOSE_PROJECT_NAME"] = compose_project_name
        values["MAINSTAY_LOCAL_IMAGE"] = mainstay_local_image
        values["SAFEBOX_IMAGE"] = safebox_image
        values["MAINSTAY_SPURLINE_IMAGE"] = spurline_image
        values["MAINSTAY_GROVE_IMAGE"] = grove_image
        values["MAINSTAY_CLEAR_IMAGE"] = clear_image
        values["MAINSTAY_DATA_PARENT"] = data_parent
        values["MAINSTAY_DATA_DIRECTORY_NAME"] = data_directory_name
        values["MAINSTAY_DATA_ROOT"] = data_root
        values["MAINSTAY_DATA_RUNTIME_USER"] = data_runtime_user
        values["MAINSTAY_LOCAL_DATA_SOURCE"] = local_data_source
        values["MAINSTAY_SAFEBOX_DATA_SOURCE"] = safebox_data_source
        values["MAINSTAY_SPURLINE_DATA_SOURCE"] = spurline_data_source
        values["MAINSTAY_GROVE_DATA_SOURCE"] = grove_data_source
        values["MAINSTAY_CLEAR_DATA_SOURCE"] = clear_data_source
        values["MAINSTAY_LOCAL_BIND_ADDRESS"] = dashboard_bind
        values["MAINSTAY_LOCAL_PORT"] = dashboard_port
        values["MAINSTAY_SAFEBOX_BIND_ADDRESS"] = safebox_bind
        values["MAINSTAY_SAFEBOX_PORT"] = safebox_port
    }
    {
        separator = index($0, "=")
        key = separator ? substr($0, 1, separator - 1) : ""
        if (key in values) {
            if (!seen[key]) {
                print key "=" values[key]
                seen[key] = 1
            }
            next
        }
        print
    }
    END {
        for (key in values) {
            if (!seen[key]) print key "=" values[key]
        }
    }
' "$recovery_file" > "$temp_file"
chmod 600 "$temp_file"
mv "$temp_file" "$env_file"
trap - EXIT HUP INT TERM

"$repo_dir/save-recovery-env.sh"
printf '%s\n' 'Recovered Mainstay configuration into this deployment directory.'
if [ "$start_after" = yes ]; then
    "$repo_dir/start-mainstay.sh"
else
    printf '%s\n' 'Run ./start-mainstay.sh when you are ready.'
fi
