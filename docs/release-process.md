---
title: Release Process
date: 2026-06-06
type: runbook
status: draft
---

# Release Process

## Fork Source Of Truth

This repository is the source of truth for the Plus workflow. Use normal,
reviewable changes in this repository; do not depend on a private-source export
or generated public mirror.

1. Run deterministic Node and Python parity gates.
2. Build and validate the Codex plugin runtime:

   ```bash
   npm run plugin:build
   npm run plugin:check
   npm run plugin:validate
   ```

3. Verify no live reports, thread URLs, credentials, or local paths are
   committed.
4. Review `git diff --check` and the final diff before opening a pull request.

## Codex Plugin Alpha

1. Confirm the marketplace file is present at `.agents/plugins/marketplace.json`.
2. Confirm the plugin manifest is present at `plugins/codex-chatgpt-control/.codex-plugin/plugin.json`.
3. Confirm the plugin exposes exactly two V1 skills:
   - `codex-chatgpt-control`
   - `chatgpt-gpt-5-6-high-consult`
   These skills must remain bundled in this one plugin; do not add a separate
   consultation plugin or marketplace entry.
4. Install locally from the checkout:

   ```bash
   codex plugin marketplace add .
   codex plugin add codex-chatgpt-control@codex-chatgpt-control
   ```

   If the marketplace already exists under a different local name, use
   `codex plugin marketplace list` and reinstall from that configured name.

5. Start a new Codex thread and verify the plugin skills are discoverable.
6. In an ordinary shell, browser-required commands should return a structured
   `browser_bridge_unavailable` blocker rather than faking browser access.
7. Run live ChatGPT smoke tests only with explicit approval and non-sensitive
   prompts.

## Trusted Publishing

When a fork-owned registry release is intentionally made, npm and PyPI releases
are published from `.github/workflows/release.yml` using GitHub Actions OIDC
trusted publishing. Do not store npm or PyPI API tokens in GitHub secrets for
this workflow.

The registry-side trusted publisher configuration must match the public
repository exactly:

- Repository: `PracticalSwan/codex-chatgpt-control-plus-subscription`
- Workflow filename: `release.yml`
- Environment: `release`
- npm package: `codex-chatgpt-control`
- PyPI project: `codex-chatgpt-control`

This fork currently retains the original package names for source
compatibility. Before enabling publication, confirm that the publisher owns
both registry names; otherwise choose fork-owned names and update manifests,
imports, commands, documentation, and release checks together. Until then,
install the source checkout or Codex plugin rather than assuming a registry
package contains the Plus workflow.

The `release` GitHub environment should require human approval. That keeps tag
creation reversible until the protected publish jobs start, while still making
the package upload itself reproducible and tokenless.

## Release Tag Flow

1. Merge the reviewed pull request after required checks pass.
2. Confirm versions and registry availability on `main`:

   ```bash
   npm run release:check-version
   npm run release:check-names
   ```

3. Create and push a `v*` tag that matches the Node package version:

   ```bash
   git tag v0.2.0-alpha.1
   git push origin v0.2.0-alpha.1
   ```

4. Approve the `release` environment deployment in GitHub Actions.
5. Let the workflow publish npm and PyPI independently. If one registry publish
   succeeds and the other fails, rerun only the failed job.
6. Verify the published packages:

   ```bash
   npm view codex-chatgpt-control version dist-tags --json
   python - <<'PY'
   import json, urllib.request
   with urllib.request.urlopen("https://pypi.org/pypi/codex-chatgpt-control/json", timeout=10) as r:
       data = json.load(r)
   print(data["info"]["version"])
   PY
   ```

## npm Alpha

1. Recheck registry state immediately before publishing:

   ```bash
   npm run release:check-version
   npm run release:check-names
   ```

2. Build and inspect the package allowlist:

   ```bash
   npm --prefix packages/node ci
   npm run node:build
   npm run node:bundle
   npm run release:check-node-pack
   ```

3. Publish through the release workflow with `--tag next`; do not publish local
   shells unless the trusted-publishing path is unavailable and the release
   owner explicitly approves a one-off fallback.

## PyPI Alpha

Best-practice backend story: keep the Node runtime as the authoritative browser backend and make Python a protocol client that launches or connects to an explicit sidecar command. For alpha, require a separately installed or locally built Node backend command. For beta, add a Python helper that discovers a trusted installed backend, such as the npm package binary or an explicitly configured command. Avoid silently embedding stale generated JavaScript in the wheel unless the export, versioning, and smoke tests prove the embedded backend and Python protocol are in lockstep.

1. Recheck registry state immediately before publishing:

   ```bash
   npm run release:check-version
   npm run release:check-names
   ```

2. Build wheel and sdist from `packages/python`.
3. Run `twine check`:

   ```bash
   python -m pip install --upgrade build twine
   rm -rf dist/python
   npm run release:build-python
   npm run release:check-python
   ```

4. Install the wheel in a fresh virtual environment.
5. Publish through the release workflow using PyPI trusted publishing.
