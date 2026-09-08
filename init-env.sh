#!/bin/sh

set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
env_file="$repo_dir/.env"
example_file="$repo_dir/.env.example"
installation_identity="$repo_dir/build/mainstay-local/installation-identity.json"
requested_data_root="${MAINSTAY_DATA_ROOT:-}"

usage() {
    printf '%s\n' 'Usage: ./init-env.sh [--data-root PATH]'
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --data-root)
            if [ "$#" -lt 2 ] || [ -z "$2" ]; then
                printf '%s\n' '--data-root requires a path.' >&2
                usage >&2
                exit 2
            fi
            requested_data_root=$2
            shift 2
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

print_reserve_advisory() {
    printf '%s\n' \
        'ADVISORY: Lightning-address delivery requires an operator-funded service-Acorn fee reserve.'
    printf '%s\n' \
        'After first startup, stop the worker and run: docker compose run --rm --no-deps service-acorn-worker python -m app.service_acorn_worker fund 100'
}

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

compose_project_name=$(read_value COMPOSE_PROJECT_NAME)
if [ -z "$compose_project_name" ]; then
    compose_project_name=mainstay-local
fi
clear_volume="${compose_project_name}_clear-data"
safebox_volume="${compose_project_name}_safebox-web-data"

configured_data_root=$(read_value MAINSTAY_DATA_ROOT)
if [ -n "$requested_data_root" ]; then
    mkdir -p "$requested_data_root"
    requested_data_root=$(CDPATH= cd -- "$requested_data_root" && pwd)
    if [ "$created" = false ] && [ -z "$configured_data_root" ]; then
        printf '%s\n' \
            'The Docker data root can only be selected during first initialization.' >&2
        printf '%s\n' \
            'Use an explicit data migration procedure for an existing installation.' >&2
        exit 1
    fi
    if [ -n "$configured_data_root" ] && \
        [ "$configured_data_root" != "$requested_data_root" ]; then
        printf '%s\n' \
            "Refusing to change MAINSTAY_DATA_ROOT from $configured_data_root." >&2
        printf '%s\n' \
            'Use an explicit data migration procedure for an existing installation.' >&2
        exit 1
    fi
    data_root=$requested_data_root
else
    data_root=$configured_data_root
fi

if [ -n "$data_root" ]; then
    case "$data_root" in
        /*) ;;
        *)
            printf '%s\n' 'MAINSTAY_DATA_ROOT must be an absolute path.' >&2
            exit 1
            ;;
    esac
    case "$data_root" in
        *:*)
            printf '%s\n' 'MAINSTAY_DATA_ROOT must not contain a colon.' >&2
            exit 1
            ;;
    esac
    configured_local_data_source=$(read_value MAINSTAY_LOCAL_DATA_SOURCE)
    if [ "$created" = false ] && [ -n "$configured_local_data_source" ]; then
        local_data_source=$configured_local_data_source
    else
        local_data_source="$data_root/mainstay-control"
    fi
    safebox_data_source="$data_root/safebox-web"
    spurline_data_source="$data_root/spurline"
    grove_data_source="$data_root/grove"
    clear_data_source="$data_root/clear"
    data_runtime_user="$(id -u):$(id -g)"
else
    local_data_source=""
    safebox_data_source=""
    spurline_data_source=""
    grove_data_source=""
    clear_data_source=""
    data_runtime_user=""
fi

ensure_data_directories() {
    if [ -n "$data_root" ]; then
        umask 077
        mkdir -p \
            "$local_data_source" \
            "$safebox_data_source" \
            "$spurline_data_source" \
            "$grove_data_source" \
            "$clear_data_source"
    fi
}

storage_has_data() {
    bind_path=$1
    volume_name=$2
    if [ -n "$data_root" ]; then
        [ -d "$bind_path" ] && \
            [ -n "$(find "$bind_path" -mindepth 1 -print -quit)" ]
        return
    fi
    docker volume inspect "$volume_name" >/dev/null 2>&1
}

master_secret=$(read_value CLEAR_MASTER_SECRET)
operator_token=$(read_value CLEAR_OPERATOR_TOKEN)
mint_service_nsec=$(read_value CLEAR_MINT_SERVICE_NSEC)
spurline_service_nsec=$(read_value SPURLINE_SERVICE_NSEC)
grove_service_nsec=$(read_value GROVE_SERVICE_NSEC)
safebox_web_service_nsec=$(read_value SAFEBOX_WEB_SERVICE_NSEC)
installation_nsec=$(read_value MAINSTAY_INSTALLATION_NSEC)
cookie_key=$(read_value SAFEBOX_COOKIE_KEY)
invite_code=$(read_value SAFEBOX_ONBOARD_INVITE_CODE)

storage_complete=true
if [ -n "$data_root" ]; then
    [ "$(read_value MAINSTAY_DATA_RUNTIME_USER)" = "$data_runtime_user" ] || storage_complete=false
    [ "$(read_value MAINSTAY_LOCAL_DATA_SOURCE)" = "$local_data_source" ] || storage_complete=false
    [ "$(read_value MAINSTAY_SAFEBOX_DATA_SOURCE)" = "$safebox_data_source" ] || storage_complete=false
    [ "$(read_value MAINSTAY_SPURLINE_DATA_SOURCE)" = "$spurline_data_source" ] || storage_complete=false
    [ "$(read_value MAINSTAY_GROVE_DATA_SOURCE)" = "$grove_data_source" ] || storage_complete=false
    [ "$(read_value MAINSTAY_CLEAR_DATA_SOURCE)" = "$clear_data_source" ] || storage_complete=false
fi

if [ -n "$master_secret" ] && [ -n "$operator_token" ] && \
    [ -n "$mint_service_nsec" ] && \
    [ -n "$spurline_service_nsec" ] && \
    [ -n "$grove_service_nsec" ] && \
    [ -n "$safebox_web_service_nsec" ] && \
    [ -n "$installation_nsec" ] && \
    [ -n "$cookie_key" ] && [ -n "$invite_code" ] && \
    [ "$storage_complete" = true ]; then
    ensure_data_directories
    chmod 600 "$env_file"
    printf '%s\n' '.env already contains the required Mainstay secrets.'
    print_reserve_advisory
    exit 0
fi

if ! command -v openssl >/dev/null 2>&1; then
    printf '%s\n' 'openssl is required to generate Mainstay secrets.' >&2
    exit 1
fi

ensure_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        printf '%s\n' \
            'Docker is required to check existing Mainstay data volumes.' >&2
        exit 1
    fi
    if ! docker info >/dev/null 2>&1; then
        printf '%s\n' \
            'Start Docker before generating identity-bound secrets.' >&2
        exit 1
    fi
}

if { [ -z "$master_secret" ] || [ -z "$cookie_key" ]; } && \
    [ -z "$data_root" ]; then
    ensure_docker
fi

if [ -z "$master_secret" ]; then
    if storage_has_data "$clear_data_source" "$clear_volume"; then
        printf '%s\n' \
            'Refusing to generate CLEAR_MASTER_SECRET because Clear data exists.' >&2
        printf '%s\n' \
            'Recover the original .env or master secret associated with that mint.' >&2
        exit 1
    fi
    master_secret=$(openssl rand -hex 32)
fi

if [ -z "$operator_token" ]; then
    operator_token=$(openssl rand -hex 32)
fi

if [ -z "$mint_service_nsec" ]; then
    mint_service_nsec=$(openssl rand -hex 32)
fi

if [ -z "$spurline_service_nsec" ]; then
    spurline_service_nsec=$(openssl rand -hex 32)
fi

if [ -z "$grove_service_nsec" ]; then
    grove_service_nsec=$(openssl rand -hex 32)
fi

if [ -z "$safebox_web_service_nsec" ]; then
    safebox_web_service_nsec=$(openssl rand -hex 32)
fi

if [ -z "$installation_nsec" ]; then
    if [ -f "$installation_identity" ]; then
        printf '%s\n' \
            'Refusing to replace the Mainstay installation identity.' >&2
        printf '%s\n' \
            "Recover MAINSTAY_INSTALLATION_NSEC for $installation_identity." >&2
        exit 1
    fi
    installation_nsec=$(openssl rand -hex 32)
fi

if [ -z "$cookie_key" ]; then
    if storage_has_data "$safebox_data_source" "$safebox_volume"; then
        printf '%s\n' \
            'Refusing to generate SAFEBOX_COOKIE_KEY because Safebox data exists.' >&2
        printf '%s\n' \
            'Recover the original .env or cookie key associated with that Safebox instance.' >&2
        exit 1
    fi
    cookie_key=$(openssl rand -base64 32 | tr '+/' '-_')
fi

if [ -z "$invite_code" ]; then
    invite_code=$(openssl rand -hex 16)
fi

umask 077
temp_file=$(mktemp "$repo_dir/.env.tmp.XXXXXX")
cleanup() {
    rm -f -- "$temp_file"
}
trap cleanup EXIT HUP INT TERM

awk \
    -v data_root="$data_root" \
    -v data_runtime_user="$data_runtime_user" \
    -v local_data_source="$local_data_source" \
    -v safebox_data_source="$safebox_data_source" \
    -v spurline_data_source="$spurline_data_source" \
    -v grove_data_source="$grove_data_source" \
    -v clear_data_source="$clear_data_source" \
    -v master_secret="$master_secret" \
    -v operator_token="$operator_token" \
    -v mint_service_nsec="$mint_service_nsec" \
    -v spurline_service_nsec="$spurline_service_nsec" \
    -v grove_service_nsec="$grove_service_nsec" \
    -v safebox_web_service_nsec="$safebox_web_service_nsec" \
    -v installation_nsec="$installation_nsec" \
    -v cookie_key="$cookie_key" \
    -v invite_code="$invite_code" '
    BEGIN {
        found_data_root = 0
        found_data_runtime_user = 0
        found_local_data = 0
        found_safebox_data = 0
        found_spurline_data = 0
        found_grove_data = 0
        found_clear_data = 0
        found_master = 0
        found_operator = 0
        found_mint_service = 0
        found_spurline_service = 0
        found_grove_service = 0
        found_safebox_web_service = 0
        found_installation = 0
        found_cookie = 0
        found_invite = 0
    }
    /^MAINSTAY_DATA_ROOT=/ {
        if (!found_data_root) {
            print "MAINSTAY_DATA_ROOT=" data_root
            found_data_root = 1
        }
        next
    }
    /^MAINSTAY_DATA_RUNTIME_USER=/ {
        if (!found_data_runtime_user) {
            print "MAINSTAY_DATA_RUNTIME_USER=" data_runtime_user
            found_data_runtime_user = 1
        }
        next
    }
    /^MAINSTAY_LOCAL_DATA_SOURCE=/ {
        if (!found_local_data) {
            print "MAINSTAY_LOCAL_DATA_SOURCE=" local_data_source
            found_local_data = 1
        }
        next
    }
    /^MAINSTAY_SAFEBOX_DATA_SOURCE=/ {
        if (!found_safebox_data) {
            print "MAINSTAY_SAFEBOX_DATA_SOURCE=" safebox_data_source
            found_safebox_data = 1
        }
        next
    }
    /^MAINSTAY_SPURLINE_DATA_SOURCE=/ {
        if (!found_spurline_data) {
            print "MAINSTAY_SPURLINE_DATA_SOURCE=" spurline_data_source
            found_spurline_data = 1
        }
        next
    }
    /^MAINSTAY_GROVE_DATA_SOURCE=/ {
        if (!found_grove_data) {
            print "MAINSTAY_GROVE_DATA_SOURCE=" grove_data_source
            found_grove_data = 1
        }
        next
    }
    /^MAINSTAY_CLEAR_DATA_SOURCE=/ {
        if (!found_clear_data) {
            print "MAINSTAY_CLEAR_DATA_SOURCE=" clear_data_source
            found_clear_data = 1
        }
        next
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
    /^CLEAR_MINT_SERVICE_NSEC=/ {
        if (!found_mint_service) {
            print "CLEAR_MINT_SERVICE_NSEC=" mint_service_nsec
            found_mint_service = 1
        }
        next
    }
    /^SPURLINE_SERVICE_NSEC=/ {
        if (!found_spurline_service) {
            print "SPURLINE_SERVICE_NSEC=" spurline_service_nsec
            found_spurline_service = 1
        }
        next
    }
    /^GROVE_SERVICE_NSEC=/ {
        if (!found_grove_service) {
            print "GROVE_SERVICE_NSEC=" grove_service_nsec
            found_grove_service = 1
        }
        next
    }
    /^SAFEBOX_WEB_SERVICE_NSEC=/ {
        if (!found_safebox_web_service) {
            print "SAFEBOX_WEB_SERVICE_NSEC=" safebox_web_service_nsec
            found_safebox_web_service = 1
        }
        next
    }
    /^MAINSTAY_INSTALLATION_NSEC=/ {
        if (!found_installation) {
            print "MAINSTAY_INSTALLATION_NSEC=" installation_nsec
            found_installation = 1
        }
        next
    }
    /^SAFEBOX_COOKIE_KEY=/ {
        if (!found_cookie) {
            print "SAFEBOX_COOKIE_KEY=" cookie_key
            found_cookie = 1
        }
        next
    }
    /^SAFEBOX_ONBOARD_INVITE_CODE=/ {
        if (!found_invite) {
            print "SAFEBOX_ONBOARD_INVITE_CODE=" invite_code
            found_invite = 1
        }
        next
    }
    { print }
    END {
        if (!found_data_root) {
            print "MAINSTAY_DATA_ROOT=" data_root
        }
        if (!found_data_runtime_user) {
            print "MAINSTAY_DATA_RUNTIME_USER=" data_runtime_user
        }
        if (!found_local_data) {
            print "MAINSTAY_LOCAL_DATA_SOURCE=" local_data_source
        }
        if (!found_safebox_data) {
            print "MAINSTAY_SAFEBOX_DATA_SOURCE=" safebox_data_source
        }
        if (!found_spurline_data) {
            print "MAINSTAY_SPURLINE_DATA_SOURCE=" spurline_data_source
        }
        if (!found_grove_data) {
            print "MAINSTAY_GROVE_DATA_SOURCE=" grove_data_source
        }
        if (!found_clear_data) {
            print "MAINSTAY_CLEAR_DATA_SOURCE=" clear_data_source
        }
        if (!found_master) {
            print "CLEAR_MASTER_SECRET=" master_secret
        }
        if (!found_operator) {
            print "CLEAR_OPERATOR_TOKEN=" operator_token
        }
        if (!found_mint_service) {
            print "CLEAR_MINT_SERVICE_NSEC=" mint_service_nsec
        }
        if (!found_spurline_service) {
            print "SPURLINE_SERVICE_NSEC=" spurline_service_nsec
        }
        if (!found_grove_service) {
            print "GROVE_SERVICE_NSEC=" grove_service_nsec
        }
        if (!found_safebox_web_service) {
            print "SAFEBOX_WEB_SERVICE_NSEC=" safebox_web_service_nsec
        }
        if (!found_installation) {
            print "MAINSTAY_INSTALLATION_NSEC=" installation_nsec
        }
        if (!found_cookie) {
            print "SAFEBOX_COOKIE_KEY=" cookie_key
        }
        if (!found_invite) {
            print "SAFEBOX_ONBOARD_INVITE_CODE=" invite_code
        }
    }
' "$source_file" >"$temp_file"

mv "$temp_file" "$env_file"
trap - EXIT HUP INT TERM
chmod 600 "$env_file"
ensure_data_directories

if [ "$created" = true ]; then
    printf '%s\n' 'Created .env with generated Mainstay secrets.'
else
    printf '%s\n' 'Added missing Mainstay secrets to .env.'
fi
print_reserve_advisory
