# AGENTS.md — Working in this repository

Context for AI agents (and humans) contributing to this **Digital.ai Release
container integration plugin**. Read this first, then see the
[Plugin Development Guide](PLUGIN_DEVELOPMENT.md) for the full how-to. There is also a
portable [`SKILL.md`](SKILL.md) that routes to both.

## What this project is

- A **container plugin** for Digital.ai Release. It contributes custom **task types**.
- Each task is a Python class in [`src/`](src/) that subclasses `BaseTask` (or `ApiBaseTask`)
  from the `digitalai-release-sdk`.
- **It is NOT a pure Python package** and is never published to PyPI. The `src/` tree is
  copied into a **Docker image** and executed there by the SDK wrapper
  (`python -m digitalai.release.integration.wrapper`, see the [`Dockerfile`](Dockerfile)).
- Building produces **two artifacts**: a **plugin zip** (type definitions + icons from
  `resources/`, installed into Release) and a **Docker image** (the `src/` code, pushed to a
  registry). The `build.sh` / `build.bat` scripts produce both.

## The one rule you must not break: the type ↔ class naming contract

Release identifies a task by its **type** (e.g. `containerExamples.Hello`). At run time the
wrapper:

1. takes the part of the type **after the dot** → `Hello`;
2. finds the `.py` file under the image that defines a class named **exactly** `Hello`;
3. imports it and calls `execute()`.

Therefore:

- The class name **after the dot must match exactly** (case-sensitive).
- Without `scriptLocation`, resolution is by class name and the file name is irrelevant.
  With `scriptLocation`, the path must point to the exact file under `src/`. Keep class names
  **unique** across `src/`.
- A type defined in [`resources/type-definitions.yaml`](resources/type-definitions.yaml)
  with no matching class (or vice-versa) is a bug.

## How to add a task (summary)

1. Declare the type in [`resources/type-definitions.yaml`](resources/type-definitions.yaml)
   (extend `containerExamples.BaseTask`; declare `input-properties` / `output-properties`).
2. Add a class in `src/` whose name matches the type after the dot; implement `execute()`.
3. Add a unit test in `tests/unit/` (and optionally a live test in `tests/integration/`).
4. Bump `VERSION` in `project.properties`, then build.

Inside `execute()`:

- `self.input_properties` — `dict` of inputs (keys = the `input-properties` names).
- `self.set_output_property(name, value)` — value must be `str`, `int`, `list`, `dict`, or `bool`.
- `self.add_comment(text)` — adds a line to the task's UI comments.
- **Raise an exception to fail the task** — the message is shown to the user. Do not swallow
  errors just to report them; the wrapper does that for you.

Use **`ApiBaseTask`** (not `BaseTask`) when the task calls the **Release** REST API: it
exposes ready-made `self.releaseApi`, `self.phaseApi`, `self.taskApi`, `self.templateApi`,
etc., all built from the task's **"Run as user"** context.

> [!NOTE]
> The `from com.xebialabs.xlrelease...` imports are real Python classes provided by the
> `digitalai-release-api-client` package (bundled with the SDK). They import fine under
> CPython — they are not Jython-only.

## Dependencies: two files, keep them in sync

- [`requirements.txt`](requirements.txt) — installed into the **Docker image** by the
  Dockerfile (`pip install`). **This is the source of truth for the container runtime.**
- [`pyproject.toml`](pyproject.toml) — the **local dev environment**, managed by `uv`.

A new **runtime** dependency must be added to **both** files. A dev-only/test dependency
goes in the `dev` extra of `pyproject.toml` only.

## Build & deploy

`build.sh` / `build.bat` read [`project.properties`](project.properties)
(`PLUGIN`, `VERSION`, `REGISTRY_URL`, `REGISTRY_ORG`), substitute the `@project.*@` /
`@registry.*@` placeholders in `resources/`, build the zip, build & push the image.

- `./build.sh` — build zip + image, push image.
- `./build.sh --zip` / `--image` — build just one.
- `./build.sh --upload` — also upload the zip to Release (configure `.xebialabs/config.yaml`).

Treat `build.sh`, `build.bat`, and the `Dockerfile` as canonical build machinery — change
them only with explicit intent. The normal release edit is bumping `VERSION` in
`project.properties`.

## Tests

- [`tests/unit/`](tests/unit/) — fast, **mocked**, no network. Run in CI.
- [`tests/integration/`](tests/integration/) — networked tests. Release-backed tests run against
  a **live** Release server and **auto-skip** when none is reachable (see
  [`tests/integration/conftest.py`](tests/integration/conftest.py)); third-party service tests
  require internet access.
- **Naming:** the test file mirrors its `src` module — `test_<module>.py` for unit tests,
  `test_<module>_live.py` for live integration tests.
- Tests are **pytest** style (plain functions + `assert`, fixtures, `parametrize`,
  `pytest.raises`), not `unittest`.

Commands (run from the repo root):

```sh
uv sync --extra dev                       # set up the env
uv run pytest                             # all tests
uv run pytest tests/unit                  # fast unit tests only
uv run pytest -m "not integration"        # same, by marker
```

Live tests read `RELEASE_SERVER_URL` / `RELEASE_USERNAME` / `RELEASE_PASSWORD`
(defaults: `http://localhost:5516`, `admin`, `admin`).

> [!TIP]
> **uv on Windows:** if uv warns that `VIRTUAL_ENV` does not match the project environment,
> target the project's env explicitly: `uv run --python .venv/Scripts/python.exe pytest`.

## Conventions & guardrails

- Match the surrounding code style; keep task classes small and single-purpose.
- Keep `type-definitions.yaml` and `src/` classes in lockstep (the naming contract).
- Don't add a runtime dep to only one of `requirements.txt` / `pyproject.toml`.
- Don't hand-edit generated build outputs (`build/`, `tmp/`) — they are produced by the scripts.
- Prefer `ApiBaseTask` wrappers over raw `get_release_api_client()` calls for Release APIs.
