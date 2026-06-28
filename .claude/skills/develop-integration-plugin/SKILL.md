---
name: develop-integration-plugin
description: Develop this Digital.ai Release container integration plugin end to end — set up the project, add new task types, write tests, and build/deploy. Use when working in this template repo for any of: first-time/clone setup and configuring project.properties; creating, adding, or scaffolding a new Release task/action (type definition in resources/type-definitions.yaml + Python class in src/ + tests); or building, packaging, publishing, releasing, deploying, or installing the plugin (build.sh / build.bat, plugin zip + Docker image).
---

# Develop a Release container integration plugin

This is the Claude Code entry point for the repository's portable skill. The content lives in
the generic root skill so it is not duplicated:

➡️ **Follow [`/SKILL.md`](../../../SKILL.md)** (the tool-neutral skill), which routes to
[AGENTS.md](../../../AGENTS.md) (conventions) and
[PLUGIN_DEVELOPMENT.md](../../../PLUGIN_DEVELOPMENT.md) (the detailed guide).

**Before acting**, read [AGENTS.md](../../../AGENTS.md) — especially the **type ↔ class naming
contract** (the type name after the dot must equal a unique class name under `src/`).
