#!/bin/sh

set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$repo_dir"

printf '%s\n' 'Pulling the latest changes...'
git pull

exec "$repo_dir/start-mainstay.sh" --force-recreate "$@"
