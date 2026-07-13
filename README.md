# codex-chatgpt-control

[![CI](https://img.shields.io/github/actions/workflow/status/PracticalSwan/codex-chatgpt-control-plus-subscription/parity.yml?branch=main&label=CI&logo=github)](https://github.com/PracticalSwan/codex-chatgpt-control-plus-subscription/actions/workflows/parity.yml)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Node](https://img.shields.io/badge/Node-20%2B-green)

Unofficial alpha SDK facade for Codex agents that need to run user-directed workflows in a visible ChatGPT web session.

https://github.com/user-attachments/assets/6ca38f2d-6646-490d-8e4d-8a6dc21e926f


## Why This Exists

This project exists because Codex and ChatGPT are useful in different parts of the same work loop. Codex is the execution environment: it can read and edit the local repo, run commands, test changes, and prepare branches. ChatGPT, meanwhile, may expose different frontier models, larger context windows, canvases, connectors, browsing/research tools, memory, or company knowledge at any given time.

In practice, that means a user can end up doing real work by hand across two surfaces:

> I am flicking between Codex for execution, and ChatGPT Plus with GPT-5.6 Sol at High Intelligence for deep planning, information gathering, consensus building, branding, and research tasks.

`codex-chatgpt-control` turns that manual tab switch into a structured, visible, user-directed bridge. It lets an agent stay inside Codex while asking ChatGPT web to help with the kinds of work where ChatGPT may currently be the stronger product surface: deep planning, long-context review, research synthesis, naming, positioning, brainstorming, design critique, and second-opinion analysis.

- **Keep Codex as home base:** preserve the local execution loop while optionally consulting ChatGPT web for planning or research-heavy steps.
- **Visible-session only:** drive chatgpt.com through a compatible Codex/browser bridge and user-visible UI controls, including file uploads and visible downloads where available.
- **Workflow primitives, not a ChatGPT API:** support prompts, thread workflows, response capture, clear stop reasons, and privacy-preserving local reports without private endpoint access.
- **Narrow by design:** built for Codex -> browser -> chatgpt.com workflows; it is not a generic browser automation framework, scraping tool, OpenAI API wrapper, or official OpenAI project.

This project is not affiliated with, endorsed by, or sponsored by OpenAI.

## Focused Plus Consultation

The bundled `chatgpt-gpt-5-6-high-consult` skill is the focused consultation
workflow for this fork. It uses the user's visible ChatGPT Plus session with
GPT-5.6 Sol at High Intelligence for planning, research, review, naming,
positioning, brainstorming, design critique, and second opinions.

- It selects GPT-5.6 Sol and High before submission, or uses only the visible
  High control when duplicate model labels make the user's already-confirmed
  GPT-5.6 Sol selection unaddressable.
- It submits a prompt once through the visible UI, then uses bounded metadata
  polling and a single Markdown read.
- A polling or browser-runtime timeout resumes the exact submitted thread;
  the prompt is never resubmitted.
- It does not select or fall back to Pro.

## What This Is For

Use `codex-chatgpt-control` when a Codex-style agent needs to work with the real ChatGPT web product that the user can see:

- start or continue visible ChatGPT threads
- submit prompts and read Markdown responses
- attach approved local files through visible upload controls
- download visible generated files
- wait for and download image-only generated artifacts
- tell the agent exactly why it could not continue when ChatGPT needs login, captcha, permissions, or UI review
- save local run reports that omit prompt and response content by default

This project deliberately does not provide hidden ChatGPT access, account automation, or a replacement for the OpenAI API.

-----

## Install This Fork

The GPT-5.6 Sol High Intelligence workflow is provided by this source checkout
and its Codex plugin. It is not published under a separate npm or PyPI package
name, so installing the upstream registry package does not install this fork's
behavior.

```bash
git clone https://github.com/PracticalSwan/codex-chatgpt-control-plus-subscription.git
cd codex-chatgpt-control-plus-subscription
npm --prefix packages/node ci
npm --prefix packages/node run build
npm --prefix packages/node run bundle
npm --prefix packages/node run bundle:backend
python -m pip install -e ./packages/python
```

The Node package is the browser-control runtime authority. The Python package
is a parity client over the same local backend protocol.

## Codex Desktop Setup

This repo includes a Codex plugin at [plugins/codex-chatgpt-control](plugins/codex-chatgpt-control). It is the easiest way to make Codex Desktop agents use this SDK consistently instead of hand-rolling browser commands.

Install the repository as a Codex plugin marketplace and add the plugin:

```bash
codex plugin marketplace add PracticalSwan/codex-chatgpt-control-plus-subscription --ref main
codex plugin add codex-chatgpt-control@codex-chatgpt-control
```

When a new version ships, refresh the marketplace snapshot and reinstall the plugin, then start a new Codex thread so updated skill metadata is loaded:

```bash
codex plugin marketplace upgrade codex-chatgpt-control
codex plugin add codex-chatgpt-control@codex-chatgpt-control
```

This repository exposes one installable Codex plugin, `codex-chatgpt-control`.
It contains:

- `codex-chatgpt-control`: the broad visible ChatGPT web workflow and diagnostics skill.
- `chatgpt-gpt-5-6-high-consult`: a focused GPT-5.6 Sol High Intelligence
  second-opinion workflow for ChatGPT Plus.
- bundled Node runtime files for bridge-enabled imports.

Install this one plugin once; do not install either skill separately or add a
separate GPT-5.6 Sol High consultation plugin.

Then add a short instruction to any repo where agents should be allowed to consult ChatGPT web:

```markdown
When a task would materially benefit from a visible ChatGPT consultation, use
the chatgpt-gpt-5-6-high-consult skill with GPT-5.6 Sol at High Intelligence.
Keep the workflow visible and user-directed; never select or fall back to Pro.
Submit once, retain the thread URL and turn baselines, and recover the same
thread after a polling or browser-runtime timeout without resubmitting. If I
say a ChatGPT thread is already open, reuse that tab with existingTab/
existing_tab instead of opening a replacement.
```

The plugin and skill are agent-facing operating guides plus local runtime bundles. They do not bundle a browser bridge, credentials, or ChatGPT account access. Real browser workflows still require a compatible Codex/browser bridge and a visible signed-in ChatGPT web session.

## Node Quick Start

Use the SDK from a Codex/browser-bridge host that provides `globalThis.agent`:

```ts
import { createChatGPT } from "codex-chatgpt-control";

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

Continue a user-open ChatGPT thread without replacing the tab:

```ts
await chatgpt.askInThread({
  thread: { type: "url", url: "https://chatgpt.com/c/<conversation-id>" },
  existingTab: true,
  prompt: "Continue from the latest answer.",
  wait: true,
  read: { format: "markdown" }
});
```

If you run browser-required commands from an ordinary shell, the safe expected result is a structured `browser_bridge_unavailable` blocker. That means the protocol path is working, but no visible browser bridge was available to the process.

Download an image-only generation through the artifact primitives:

```ts
await chatgpt.artifacts.wait({
  kind: "image",
  requireDownload: true
});

const downloaded = await chatgpt.artifacts.downloadLatest({
  destDir: "/absolute/output/dir"
});
```

Generated images are artifacts, not assistant text. `messages.readLatest()` can
correctly return `not_found` for an image-only result while
`artifacts.downloadLatest()` still saves the image. If a claimed user-open tab's
bridge session is stale, artifact export may recover by reopening the same saved
`https://chatgpt.com/c/...` conversation in a temporary bridge-owned tab and
using the bridge page-assets inventory. This recovery is fallback-only; normal
text/thread commands do not automatically replace the user's tab.

## Python Quick Start

The Python package talks to the local Node backend built from this checkout.
Run the source installation steps above first, then point Python at that bundle:

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

## Quick Start From Source

Clone the repo and run the deterministic source checks:

```bash
git clone https://github.com/PracticalSwan/codex-chatgpt-control-plus-subscription.git
cd codex-chatgpt-control-plus-subscription
npm --prefix packages/node ci
npm --prefix packages/node test
npm --prefix packages/node run build
npm --prefix packages/node run bundle
npm --prefix packages/node run bundle:backend
```

Use the built source bundle from a Codex/browser-bridge host:

```ts
import { createChatGPT } from "./dist/codex-chatgpt-control.bundle.mjs";

const chatgpt = createChatGPT({ agent: globalThis.agent });
```

-----

![codex-chatgpt-control visible-session bridge banner](assets/readme/codex-chatgpt-control-readme-banner.png)

## SDK Shape

The main Node entrypoint is `createChatGPT({ agent })`. It exposes:

- `chatgpt.agent(...)` and `chatgpt.runner.run(...)` for Agents-style visible-session workflows.
- `chatgpt.ask(...)`, `askInThread(...)`, `askWithFiles(...)`, and `askAndDownload(...)` for common task flows.
- `chatgpt.responses.create(...)` for a narrow Responses-shaped adapter over the same visible browser runner.
- Primitive groups for `session`, `threads`, `messages`, `artifacts`, `files`, `modes`, `tools`, and `response`.
- Discovery helpers: `chatgpt.help()`, `chatgpt.commands()`, and `chatgpt.describe(name)`.
- Local run reports through `chatgpt.createReport(...)` and `chatgpt.reports`; prompt and response content is omitted unless explicitly enabled.

Useful repo links:

- [Bundled Codex skill](skills/codex-chatgpt-control/SKILL.md)
- [Architecture](docs/architecture.md)
- [Browser bridge](docs/browser-bridge.md)
- [Safety model](docs/safety.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Release process](docs/release-process.md)
- [Python examples](packages/python/examples/)

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

Attachment paths must be absolute on the machine running the Node backend. Use `/home/you/file.pdf` or `/mnt/c/work/file.pdf` for Linux/WSL backends. Use `C:\Users\you\file.pdf` or `\\server\share\file.pdf` for Windows backends. The backend rejects ambiguous Windows forms such as `C:Users\you\file.pdf` and rejects Windows-looking paths when the backend host is POSIX.

File attachments need two separate permission gates:

1. **Chrome extension gate:** open `chrome://extensions`, choose the Codex/browser bridge extension, open **Details**, and enable **Allow access to file URLs**.
2. **Codex app gate:** in Codex settings, allow Google Chrome uploads under **Computer Use > Google Chrome > Permissions > Uploads**. Choose the most restrictive setting that still fits your workflow; for unattended local smoke tests, use the setting that always allows uploads.

If either gate is missing, file upload workflows should stop with a structured permission blocker instead of retrying blindly.

## Repository Layout

```text
skills/             Public Codex skill for agent-facing usage
packages/node/      TypeScript runtime, contracts, backend server, tests
packages/python/    Python parity client, examples, tests
docs/               Public architecture, safety, bridge, and release notes
.github/workflows/  Deterministic CI gates
```

-----

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
npm run docs:drift
npm run parity:fixtures
npm run parity:suite
```

Run deterministic Python gates after the backend bundle exists:

```bash
cd packages/python
python -m pip install -e .[dev]
python -m unittest discover -s tests
python -m compileall -q src examples
python -m pyright src tests
python scripts/live_smoke.py --mode ordinary-shell
```

Ordinary-shell smoke checks are expected to return structured browser-bridge blockers for browser-required actions. A real ChatGPT run requires a compatible visible browser session and bridge.

## Package Identities

This fork retains the original package/import identities for source compatibility,
but does not claim that the upstream registry packages contain its changes.

- Node package/import: `codex-chatgpt-control`
- Python package/import: `codex-chatgpt-control` / `codex_chatgpt_control`
- Node import: `import { createChatGPT } from "codex-chatgpt-control";`
- Python import: `import codex_chatgpt_control`

## Safety

Do not use this project to bypass login, access hidden endpoints, scrape private data, or automate activity outside a user-directed visible session. See [docs/safety.md](docs/safety.md) and [SECURITY.md](SECURITY.md).
