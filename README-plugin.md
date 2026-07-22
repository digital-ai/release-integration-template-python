<!--
  Starter README for a plugin generated from the Release integration template.
  After cloning the template, replace the template's README with this file:

      mv README-plugin.md README.md      # (Windows: move /Y README-plugin.md README.md)

  Then fill in the placeholders below: the title, the one-line description, and the
  plugin name in `project.properties`.
-->

# <Your Plugin Name>

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
[![digitalai-release-sdk](https://img.shields.io/badge/digitalai--release--sdk-PyPI-orange)](https://pypi.org/project/digitalai-release-sdk/)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

<!-- One line on what this plugin does. -->
A Digital.ai Release **container plugin**. It contributes custom **task types** — each is a
Python class in [`src/`](src/) that is packaged into a Docker image and run by Release as a
container task. Built from the
[Release integration template](https://github.com/digital-ai/release-integration-template-python).

The task code is built on the **[`digitalai-release-sdk`](https://pypi.org/project/digitalai-release-sdk/)** —
tasks subclass its `BaseTask` (or `ApiBaseTask`) to read inputs, set outputs, and call the Release APIs.
It is the project's main dependency and is pinned in [`requirements.txt`](requirements.txt).

Building this project produces **two artifacts**:

- a **plugin zip** — the plugin metadata from `resources/`, installed into Release.
- a **Docker image** — the `src/` task code and its dependencies, pushed to a container registry and run by Release.

> [!TIP]
> **Adding or changing tasks?** See the **[Plugin Development Guide](docs/PLUGIN_DEVELOPMENT.md)** —
> it explains how a container plugin works, how to add a task, and the type ↔ class naming contract.

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
automatically when none is reachable. Point Release-backed tests at a server
(defaults shown) with:

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

The `--image`, default, and `--upload` workflows require Docker to be running and
the registry in `REGISTRY_URL` to be reachable. For the local Docker Compose
environment, start the stack first and add `127.0.0.1 container-registry` to your
hosts file as described in [Run Release locally](#run-release-locally). For a remote
registry, make sure Docker is authenticated and that `REGISTRY_URL` and
`REGISTRY_ORG` in [`project.properties`](project.properties) are correct.

| Command                | Result                                                        |
|------------------------|---------------------------------------------------------------|
| `./build.sh`           | Build the zip **and** the image, and push the image.          |
| `./build.sh --zip`     | Build only the plugin zip.                                    |
| `./build.sh --image`   | Build only the Docker image and push it.                      |
| `./build.sh --upload`  | Build the zip and image, push the image, and upload the zip to Release. |

On Windows, use `build.bat` with the same arguments, for example:

```powershell
.\build.bat --upload
```

## Install the plugin into Release

**Option A — command line**

Set your Release server details in [`.xebialabs/config.yaml`](.xebialabs/config.yaml),
then make sure the Release server is running and use the command for your platform:

```sh
# macOS / Linux
./build.sh --upload
```

```powershell
# Windows
.\build.bat --upload
```

**Option B — Release UI**

In the Release **Plugin Manager**, upload the zip from `build/`
(named `<PLUGIN>-<VERSION>.zip`, using the values in [`project.properties`](project.properties)),
then reload the browser.

## First successful run

Use this sequence to verify the complete local workflow:

1. Start the local Release and registry with `docker compose up -d --build`.
2. Wait for `Digital.ai Release has started.` in the Release container logs.
3. Add `127.0.0.1 container-registry` to your hosts file.
4. Build and install the plugin with `./build.sh --upload` or `.\build.bat --upload` on Windows.
5. Open <http://localhost:5516>, create a template, and add one of your task types.
6. Run the release and verify the task produces the expected output.

## Clean up the local environment

When you finish testing, stop the local Release server, runner, and registry:

```sh
docker compose down
```

This stops the containers but preserves the local registry/server data mounted under
`dev-environment/`. To reset the development environment and remove that test state,
run `docker compose down` and remove the generated contents under that directory before
starting the stack again.

## Related resources

- **[Digital.ai Release API Client Documentation](https://github.com/digital-ai/release-api-client-python/blob/main/docs/README.md)** —
  API Classes and Models reference for the Python client library.
- **[Digital.ai Python SDK Documentation](https://docs.digital.ai/release/docs/how-to/overview-python-sdk)** —
  Comprehensive guide to using the Python SDK and building custom tasks.
- **[Digital.ai Release Python SDK](https://pypi.org/project/digitalai-release-sdk/)** —
  The official SDK package for integrating with Digital.ai Release, on PyPI.

## License

See [LICENSE.md](LICENSE.md).
