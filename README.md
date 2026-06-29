# Template Project for Digital.ai Release Integrations

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
[![digitalai-release-sdk](https://img.shields.io/badge/digitalai--release--sdk-PyPI-orange)](https://pypi.org/project/digitalai-release-sdk/)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

This project serves as a template for developing a Python-based **container plugin**
for Digital.ai Release. Each task is a Python class in [`src/`](src/) that is packaged
into a Docker image and run by Release as a container task.

The task code is built on the **[`digitalai-release-sdk`](https://pypi.org/project/digitalai-release-sdk/)** —
tasks subclass its `BaseTask` (or `ApiBaseTask`) to read inputs, set outputs, and call the Release APIs.
It is the project's main dependency and is pinned in [`requirements.txt`](requirements.txt).

Building the project produces **two artifacts**:

- a **plugin zip** — the plugin metadata from `resources/`, installed into Release.
- a **Docker image** — the `src/` task code and its dependencies, pushed to a container registry and run by Release.

> [!TIP]
> **Writing your own tasks?** Start with the **[Plugin Development Guide](docs/PLUGIN_DEVELOPMENT.md)** —
> it explains how a container plugin works, how to add a task, and how each bundled example was built.

## Contents

- [Quick start](#quick-start)
- [Project layout](#project-layout)
- [Prerequisites](#prerequisites)
- [Development](#development)
- [Run Release locally](#run-release-locally)
- [Build & publish](#build--publish)
- [Install the plugin into Release](#install-the-plugin-into-release)
- [Try it out](#try-it-out)
- [Related resources](#related-resources)
- [License](#license)

## Quick start

```sh
uv sync --extra dev                  # set up the local env (.venv)
docker compose up -d --build         # local Release server at http://localhost:5516
```

Then create a template with the **Hello** task and run it. Each step is detailed below.

## Project layout

| Path                  | Purpose                                                                       |
|-----------------------|-------------------------------------------------------------------------------|
| `src/`                | Task implementations. **This code ships inside the Docker image.** See the [Plugin Development Guide](docs/PLUGIN_DEVELOPMENT.md). |
| `tests/`              | Tests for the task classes — `unit/` (fast) and `integration/` (network). Not shipped in the image. |
| `resources/`          | Plugin metadata (`type-definitions.yaml`, icons) packaged into the plugin zip. |
| `requirements.txt`    | Runtime dependencies installed into the Docker image. **Source of truth for the container.** |
| `pyproject.toml`      | Local development environment, managed by [uv](https://docs.astral.sh/uv/).   |
| `Dockerfile`          | Builds the container image that runs the tasks.                               |
| `build.sh` / `build.bat` | Builds the plugin zip and the Docker image, and uploads them to Release.    |
| `project.properties`  | Plugin name, version, and registry coordinates used by the build scripts.     |
| `docker-compose.yaml` | A local Dockerized Release server (+ container registry) for testing.          |
| `dev-environment/`    | Build contexts and config used by `docker-compose.yaml`.                       |
| `docs/`               | Contributor docs: `PLUGIN_DEVELOPMENT.md` (detailed guide), `AGENTS.md` (conventions/guardrails for AI agents), and `SKILL.md` (portable `develop-release-integration` skill that routes to the docs above). |

> [!NOTE]
> This is **not** a pure Python package — it is not published to PyPI.
> The `src/` tree is copied into a Docker image and executed there by the
> Release task wrapper.

## Prerequisites

- [Python 3.10+](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/) — for the local development environment
- [Docker](https://www.docker.com/) — to build and run the container image
- [Git](https://git-scm.com/)

Install uv:

```sh
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Development

This project uses **uv** to manage a local virtual environment for writing and
testing tasks. The container image itself is built from `requirements.txt` (see
[Build & publish](#build--publish)).

### Set up the environment

```sh
# Creates .venv and installs runtime + dev dependencies
uv sync --extra dev
```

### Run the tests

Tests are split into [`tests/unit/`](tests/unit/) (fast, no external dependencies) and
[`tests/integration/`](tests/integration/) (hit the network or external services, and are
also marked with `@pytest.mark.integration`).

```sh
# Run every test
uv run pytest

# Run only the fast unit tests
uv run pytest tests/unit          # or: uv run pytest -m "not integration"
```

Integration tests that need a live Digital.ai Release server skip themselves
automatically when none is reachable. Some integration tests call external
services directly, so they require internet access. Point Release-backed tests at
a server (defaults shown) with:

```sh
# macOS / Linux
RELEASE_SERVER_URL=http://localhost:5516 RELEASE_USERNAME=admin RELEASE_PASSWORD=admin uv run pytest tests/integration
```

```powershell
# Windows (PowerShell)
$env:RELEASE_SERVER_URL="http://localhost:5516"; $env:RELEASE_USERNAME="admin"; $env:RELEASE_PASSWORD="admin"; uv run pytest tests/integration
```

### Add a dependency

Because the container is built from `requirements.txt`, a new **runtime**
dependency must be added in **two** places so local dev matches the image:

1. Add it to `requirements.txt` (used by the Dockerfile).
2. Add it to `pyproject.toml`, then refresh the lockfile:

   ```sh
   uv add <package>     # updates pyproject.toml and uv.lock
   ```

A dev-only dependency (e.g. a test helper) goes in the `dev` extra only:

```sh
uv add --optional dev <package>
```

## Run Release locally

Run a local Release server, with its own container registry, using Docker.

```sh
docker compose up -d --build
```

### Configure your `hosts` file

Release must be able to reach the local container registry by name. Add this entry:

- **macOS / Linux** — `/etc/hosts` (requires `sudo`)
- **Windows** — `C:\Windows\System32\drivers\etc\hosts` (run as administrator)

```
127.0.0.1 container-registry
```

## Build & publish

The build scripts read `project.properties`, build the plugin zip from
`resources/`, build the Docker image from the `Dockerfile`, and push the image to
the configured registry.

| Command                | Result                                                        |
|------------------------|---------------------------------------------------------------|
| `./build.sh`           | Build the zip **and** the image, and push the image.          |
| `./build.sh --zip`     | Build only the plugin zip.                                    |
| `./build.sh --image`   | Build only the Docker image and push it.                      |
| `./build.sh --upload`  | Build the zip and image, push the image, and upload the zip to Release. |

On Windows, use `build.bat` with the same arguments.

## Install the plugin into Release

**Option A — command line**

Set your Release server details in [`.xebialabs/config.yaml`](.xebialabs/config.yaml), then:

```sh
./build.sh --upload        # build.bat --upload on Windows
```

**Option B — Release UI**

In the Release **Plugin Manager**, upload the zip from `build/`
(named `<PLUGIN>-<VERSION>.zip`, e.g. `publisher-release-target-integration-0.0.1.zip`
with the current [`project.properties`](project.properties)),
then reload the browser.

## Try it out

Create a template with the **Hello** task (`containerExamples.Hello`) and run it.

When you are done, stop the local environment:

```sh
docker compose down
```

## Related resources

- **[Digital.ai Release API Client Documentation](https://github.com/digital-ai/release-api-client-python/blob/main/docs/README.md)** —
  API Classes and Models reference for the Python client library.
- **[Digital.ai Python SDK Documentation](https://docs.digital.ai/release/docs/how-to/overview-python-sdk)** —
  Comprehensive guide to using the Python SDK and building custom tasks.
- **[SDK Template Project for integration plugins](https://github.com/digital-ai/release-integration-template-python)** —
  A starting point for building custom integrations using Digital.ai Release and Python.
- **[Digital.ai Release Python SDK](https://pypi.org/project/digitalai-release-sdk/)** —
  The official SDK package for integrating with Digital.ai Release, on PyPI.

## License

See [LICENSE.md](LICENSE.md).
