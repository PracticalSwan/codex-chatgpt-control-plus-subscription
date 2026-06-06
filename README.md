# codex-chatgpt-control

[![CI](https://img.shields.io/github/actions/workflow/status/adamallcock/codex-chatgpt-control/parity.yml?branch=main&label=CI&logo=github)](https://github.com/adamallcock/codex-chatgpt-control/actions/workflows/parity.yml)
![release](https://img.shields.io/badge/release-source%20alpha-orange)
![npm](https://img.shields.io/badge/npm-not%20published-lightgrey?logo=npm)
![PyPI](https://img.shields.io/badge/pypi-not%20published-lightgrey?logo=pypi)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Node](https://img.shields.io/badge/Node-20%2B-green)

Unofficial alpha SDK facade for Codex agents that need to run user-directed workflows in a visible ChatGPT web session.

## Why This Exists

This project exists because Codex and ChatGPT are useful in different parts of the same work loop. Codex is the execution environment: it can read and edit the local repo, run commands, test changes, and prepare branches. ChatGPT, meanwhile, may expose different frontier models, Pro-tier reasoning modes, larger context windows, canvases, connectors, browsing/research tools, memory, or company knowledge at any given time.

In practice, that means a user can end up doing real work by hand across two surfaces:

> I am flicking between Codex for execution, and ChatGPT with Pro for deep planning, information gathering, consensus building, branding, and research tasks.

`codex-chatgpt-control` turns that manual tab switch into a structured, visible, user-directed bridge. It lets an agent stay inside Codex while asking ChatGPT web to help with the kinds of work where ChatGPT may currently be the stronger product surface: deep planning, long-context review, research synthesis, naming, positioning, brainstorming, design critique, and second-opinion analysis.

- **Keep Codex as home base:** preserve the local execution loop while optionally consulting ChatGPT web for planning or research-heavy steps.
- **Visible-session only:** drive chatgpt.com through a compatible Codex/browser bridge and user-visible UI controls, including file uploads and visible downloads where available.
- **Workflow primitives, not a ChatGPT API:** support prompts, thread workflows, response capture, structured blockers, and redacted run reports without private endpoint access.
- **Narrow by design:** built for Codex -> browser -> chatgpt.com workflows; it is not a generic browser automation framework, scraping tool, OpenAI API wrapper, or official OpenAI project.

This project is not affiliated with, endorsed by, or sponsored by OpenAI.

## Status

This repository is public-source alpha preparation. npm and PyPI packages are not published yet. The Node package is the runtime authority; the Python package is a parity client over the same backend protocol.

## What This Is For

Use `codex-chatgpt-control` when a Codex-style agent needs to work with the real ChatGPT web product that the user can see:

- start or continue visible ChatGPT threads
- submit prompts and read Markdown responses
- attach approved local files through visible upload controls
- download visible generated files
- return structured blockers for login, captcha, permissions, selector drift, or missing browser bridge
- create redacted run reports

This project deliberately does not provide hidden ChatGPT access, account automation, or a replacement for the OpenAI API.

## Quick Start From Source

Clone the repo and build the Node runtime:

```bash
git clone https://github.com/adamallcock/codex-chatgpt-control.git
cd codex-chatgpt-control/packages/node
npm ci
npm test
npm run build
npm run bundle
npm run bundle:backend
```

Use the SDK from a Codex/browser-bridge host that provides `globalThis.agent`:

```ts
import { createChatGPT } from "./dist/codex-chatgpt-control.bundle.mjs";

const chatgpt = createChatGPT({ agent: globalThis.agent });
const reviewer = chatgpt.agent({
  name: "reviewer",
  instructions: "Review carefully and return Markdown."
});

const result = await chatgpt.runner.run(reviewer, {
  input: "Reply with a one-sentence summary of this project.",
  thread: { type: "new" },
  response: { format: "markdown" }
});

console.log(result.output_text);
```

If you run browser-required commands from an ordinary shell, the safe expected result is a structured `browser_bridge_unavailable` blocker. That means the protocol path is working, but no visible browser bridge was available to the process.

## Bundled Codex Skill

This repo includes a public Codex skill at [skills/codex-chatgpt-control/SKILL.md](skills/codex-chatgpt-control/SKILL.md).

Install it into a local Codex skills directory:

```bash
mkdir -p ~/.codex/skills/codex-chatgpt-control
rsync -a skills/codex-chatgpt-control/ ~/.codex/skills/codex-chatgpt-control/
```

The skill is an agent-facing operating guide. It does not bundle a private browser bridge or credentials. Build the Node runtime from `packages/node` first, then point the skill/user workflow at that local source checkout until registry packages are published.

## Runtime Requirements

For deterministic tests and ordinary-shell protocol checks:

- Node.js 20 or newer for `packages/node`
- Python 3.10 or newer for `packages/python`
- npm for Node dependency installation
- Python virtualenv tooling for Python development

For real ChatGPT browser control:

- a signed-in ChatGPT web session in Chrome
- a compatible Codex/browser bridge that exposes `globalThis.agent`
- a visible browser tab or permission to open one
- user approval for prompts, files, downloads, and any account-affecting action

`globalThis.agent` is not created by this package. It must come from the host runtime, such as a Codex environment with a compatible browser bridge. The SDK refuses to fake this path: ordinary shell runs should return `browser_bridge_unavailable` for browser-required operations.

### Local File Upload Requirements

File attachments need two separate permission gates:

1. **Chrome extension gate:** open `chrome://extensions`, choose the Codex/browser bridge extension, open **Details**, and enable **Allow access to file URLs**.
2. **Codex app gate:** in Codex settings, allow Google Chrome uploads under **Computer Use > Google Chrome > Permissions > Uploads**. Choose the most restrictive setting that still fits your workflow; for unattended local smoke tests, use the setting that always allows uploads.

If either gate is missing, file upload workflows should stop with a structured permission blocker instead of retrying blindly.

## Python Quick Start

Build the Node backend first:

```bash
cd packages/node
npm ci
npm run bundle:backend
```

Install the Python package from source:

```bash
cd ../python
python -m pip install -e .[dev]
python scripts/live_smoke.py --mode ordinary-shell
```

Use Python against an explicit backend command:

```python
from codex_chatgpt_control import Agent, BackendClient, Runner, StdioBackendTransport

backend = BackendClient(StdioBackendTransport(
    command=["node", "../node/dist/codex-chatgpt-control-backend.mjs"]
))
runner = Runner(backend)

try:
    result = runner.run_sync(
        Agent(name="reviewer", instructions="Review carefully."),
        {
            "input": "Reply with hi.",
            "thread": {"type": "new"},
            "response": {"format": "markdown"},
        },
    )
finally:
    backend.close()

print(result.status)
print(result.output_text)
```

The Python package is a protocol client. The current browser runtime is still Node-backed.

## Repository Layout

```text
skills/             Public Codex skill for agent-facing usage
packages/node/      TypeScript runtime, contracts, backend server, tests
packages/python/    Python parity client, examples, tests
docs/               Public architecture, safety, bridge, and release notes
.github/workflows/  Deterministic CI gates
```

## Development

Run deterministic Node gates:

```bash
cd packages/node
npm ci
npm test
npm run build
npm run bundle
npm run bundle:backend
npm run contract:validate
npm run parity:fixtures
```

Run deterministic Python gates after the backend bundle exists:

```bash
cd packages/python
python -m pip install -e .[dev]
python -m unittest discover -s tests
python -m compileall -q src examples
python -m pyright --pythonpath "$(which python)" src tests
python scripts/live_smoke.py --mode ordinary-shell
```

Ordinary-shell smoke checks are expected to return structured browser-bridge blockers for browser-required actions. A real ChatGPT run requires a compatible visible browser session and bridge.

## Packages

- npm target: `codex-chatgpt-control`
- PyPI target: `codex-chatgpt-control`
- Python import: `codex_chatgpt_control`

The package manifests intentionally stay alpha-gated. Remove npm `"private": true` only when the package allowlist, install smoke, and trusted publisher setup are complete.

## Safety

Do not use this project to bypass login, access hidden endpoints, scrape private data, or automate activity outside a user-directed visible session. See [docs/safety.md](docs/safety.md) and [SECURITY.md](SECURITY.md).
