# Mainstay

Mainstay is the future unified local-first application for records, identity,
payments, and community resource coordination. It brings the Safebox, Acorn,
Stroma, Grove, Spurline, and Clear product family into one coherent experience across
connected and disrupted conditions.

Mainstay is the application. Lockbox is the appliance. There's no place like
home.

## Documentation

Design notes:

- [mainstay-local Hypervisor and FIPS](docs/LOCAL-FIRST-HYPERVISOR-AND-FIPS-DESIGN-NOTE.md)

## Prototype App

The first `mainstay-local` prototype lives in `app/`. Install the local
development environment with Poetry:

```bash
poetry install --with dev,docs
```

Then run the CLI from this checkout:

```bash
poetry run mainstay-local init
poetry run mainstay-local config
poetry run mainstay-local status
```

It starts as a thin endpoint registry and lifecycle wrapper. The Mainstay
Compose project is being assembled one service at a time, beginning with
Spurline and Grove. Safebox Web remains one managed app inside the local
runtime.

Run the local control-plane HTTP surface directly:

```bash
poetry run mainstay-local serve --host 127.0.0.1 --port 8788
```

Then open:

```text
http://127.0.0.1:8788/health
http://127.0.0.1:8788/registry
http://127.0.0.1:8788/status
```

Run the tests and linter:

```bash
poetry run pytest
poetry run ruff check .
```

## Run with Docker

Create `.env` from `.env.example`, then start the local control plane with its
private Spurline relay and Grove Blossom server. The `spurline` and `grove`
checkouts must be beside the `mainstay` checkout because Compose builds them
from sibling directories:

```bash
cp .env.example .env
docker compose up --build --detach
docker compose ps
curl http://127.0.0.1:8788/health
```

Spurline is reachable by Mainstay containers as `ws://spurline:8080`; Grove is
reachable as `http://grove:8000`. Neither publishes a host port in the default
deployment. For direct diagnostics from the Docker host, apply the debug
overlay:

```bash
docker compose -f docker-compose.yaml \
  -f docker-compose.debug-ports.yaml up --build --detach
curl http://127.0.0.1:8780/health
curl http://127.0.0.1:8001/health
```

The names `spurline` and `grove` are Compose network aliases, not durable
service identities. Containers and volumes use Compose project-scoped names,
allowing these instances to coexist with separately deployed containers.
Grove's debug port does not change its bundle origin or BUD-11 server name.
Safebox Web and Clear remain registered but disabled until each is added to the
Mainstay Compose project.

The Docker default publishes port `8788` on `0.0.0.0` so another trusted
machine on the LAN or VPN can reach Mainstay Local:

```text
http://<host-address>:8788/
http://<host-address>:8788/status
```

Use a host firewall or VPN ACL when the host has interfaces that should not
reach the control plane.

On a deployment host, pull, rebuild, recreate, and check the managed service
bundle with:

```bash
./refresh-containers.sh
```

Install and preview the MkDocs site locally:

```bash
poetry install --with docs
poetry run mkdocs serve
```

Then open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

The published site is [trbouma.github.io/mainstay](https://trbouma.github.io/mainstay/).

## Status

Mainstay is currently a product vision and integration direction. The sibling
components are being developed and proven independently before they are
assembled into the unified application.

## License

MIT
