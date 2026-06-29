---
name: develop-release-integration
description: Build, test, and maintain this container-based integration plugin for Digital.ai Release (Python SDK). Use for project setup, defining task types and server connections in resources/type-definitions.yaml, implementing tasks in src/, writing pytest tests, and the build/deploy workflow. Routes to the detailed guide; does not duplicate it.
license: MIT
metadata:
  audience: developers
  workflow: digital-ai-release
---

# Develop a Release container integration plugin

A portable, tool-neutral skill for working in this template. It is concise on purpose: the
**authoritative content lives in the repo docs**, and this file routes you to the right one so
nothing is duplicated or drifts.

- **[AGENTS.md](AGENTS.md)** — conventions and guardrails. **Read first.**
- **[PLUGIN_DEVELOPMENT.md](PLUGIN_DEVELOPMENT.md)** — the detailed guide (architecture, type
  definitions, task patterns, examples, dev environment, troubleshooting, Kubernetes).
- **[README.md](README.md)** — setup, build, and install commands.

## What this covers

Setting up the project · defining task types and server connections in
`resources/type-definitions.yaml` · implementing tasks in `src/` · writing pytest tests ·
building the plugin zip + Docker image and installing into Release.

## The one rule you must not break

A task's **type** maps to its Python **class** by the name after the dot
(`containerExamples.Reverse` → class `Reverse`). The class name must match **exactly** and be
**unique** across `src/`. Without `scriptLocation`, resolution is by class name; with
`scriptLocation`, the path must point to the exact file under `src/`.
→ [details](AGENTS.md#the-one-rule-you-must-not-break-the-type--class-naming-contract)

## Route the request

| To… | Go to |
|-----|-------|
| Set up / configure a fresh clone | [README → Development](README.md#development); name the plugin in `project.properties`; `uv sync --extra dev`. |
| Add a new task | [PLUGIN_DEVELOPMENT.md → Add a new task](PLUGIN_DEVELOPMENT.md#add-a-new-task--step-by-step) (declare type → write class → test → build). |
| Understand the SDK task API or examples | [PLUGIN_DEVELOPMENT.md → Anatomy of a task](PLUGIN_DEVELOPMENT.md#anatomy-of-a-task) and [The example tasks explained](PLUGIN_DEVELOPMENT.md#the-example-tasks-explained). |
| Build / deploy / install | [AGENTS.md → Build & deploy](AGENTS.md#build--deploy) and [README → Build & publish](README.md#build--publish). |
| Run the dev server or fix a stuck server | [PLUGIN_DEVELOPMENT.md → The development environment](PLUGIN_DEVELOPMENT.md#the-development-environment) and [Troubleshooting](PLUGIN_DEVELOPMENT.md#troubleshooting). |

## Always

- Keep `resources/type-definitions.yaml` and `src/` classes in lockstep (the naming contract).
- Add a runtime dependency to **both** `requirements.txt` (image) and `pyproject.toml` (dev).
- Tests are **pytest** in `tests/unit` (fast) and `tests/integration` (networked; Release-backed
  tests auto-skip, third-party service tests require internet access).
  Run `uv run pytest` before building (on Windows, add `--python .venv/Scripts/python.exe` if
  uv warns about `VIRTUAL_ENV`).
