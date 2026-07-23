---
title: Troubleshooting
date: 2026-06-06
type: reference
status: draft
---

# Troubleshooting

<!-- surface-drift:blocker-kind-coverage:start -->
## Blocker Kind Coverage

This section is checked by `npm run docs:drift`. Keep it aligned with `BlockerKind`, `explainCommandBlocker(...)`, command descriptors, and public troubleshooting coverage.

- `browser_bridge_unavailable`: Browser bridge unavailable (category: `environment`, severity: `blocked`, user action: no)
- `login_required`: Login required (category: `auth`, severity: `action_required`, user action: yes)
- `captcha`: Captcha or human verification required (category: `auth`, severity: `action_required`, user action: yes)
- `rate_limit`: Rate limited (category: `auth`, severity: `action_required`, user action: yes)
- `modal`: Modal is blocking the page (category: `runtime`, severity: `action_required`, user action: yes)
- `permission`: Permission required (category: `permission`, severity: `action_required`, user action: yes)
- `confirmation`: Confirmation required (category: `user_confirmation`, severity: `action_required`, user action: yes)
- `selector_drift`: Selector drift (category: `ui_drift`, severity: `blocked`, user action: no)
- `artifact_unavailable`: Artifact unavailable (category: `artifact`, severity: `warning`, user action: no)
- `artifact_selector_drift`: Artifact selector drift (category: `ui_drift`, severity: `blocked`, user action: no)
- `artifact_download_unavailable`: Artifact download unavailable (category: `download`, severity: `warning`, user action: no)
- `download_unavailable`: Download unavailable (category: `download`, severity: `warning`, user action: no)
- `upload_failed`: Upload failed (category: `upload`, severity: `action_required`, user action: yes)
- `not_found`: Target not found (category: `not_found`, severity: `warning`, user action: no)
- `unknown`: Unknown blocker (category: `unknown`, severity: `blocked`, user action: no)
<!-- surface-drift:blocker-kind-coverage:end -->

## `browser_bridge_unavailable`

Expected from ordinary shells. Use it as a diagnostic that the command failed safely before touching browser state.

For a real browser run, verify:

- Chrome is open and signed in to ChatGPT.
- The host runtime exposes `globalThis.agent`.
- The browser bridge can claim or open a visible ChatGPT tab.

## Python Backend Bundle Missing

Run from `packages/node`:

```bash
npm ci
npm run bundle:backend
```

Then rerun the Python smoke from `packages/python`.

## Selector Drift

Treat selector drift as a product-change blocker. Capture the smallest public-safe reproduction and update selectors/tests together.

## GPT-5.6 Sol High Consultation Recovery

Focused consultations submit exactly once. Save the claimed tab id, canonical
thread URL when available, and the pre-submit total and assistant turn counts.
If polling or the browser kernel times out, wait eight seconds, reconnect to
the same visible thread, then resume bounded `messages.wait(...)` recovery with
the original baselines and strict
`completionGate: { start: "<Start>", end: "<End>" }`. Never submit the prompt
again.

The focused prompt requires each marker exactly once and substantive content
between them. A stable response with no `<End>`, a preamble before `<Start>`,
duplicate markers, or an empty body is still incomplete. Keep polling the exact
thread until `data.completionGate.status` is `complete`, then read unclipped
`visible_text` and independently verify the same envelope and advanced turn
counts. If the overall recovery budget expires, report the exact thread URL
and blocker instead of claiming success.

The first post-submit URL may be a provisional `/c/WEB:...` value. Keep polling
the claimed page until command context exposes a canonical
`https://chatgpt.com/c/<conversation-id>` URL; never use the provisional value
for a recovery reopen. If the runtime fails first, reclaim only the saved tab
id, require both turn counts to advance beyond their baselines, then save and
reopen its canonical URL. Block if any of those checks fail.

Do not use a clipped `maxChars` read to validate the end boundary. Markdown or
HTML serialization can also be unsuitable for literal angle-bracket gates; use
the direct visible-text capture for final validation.

The current Plus mode picker may show `GPT-5.6 Sol` and `High` while the
composer reports only `High` after selection. That is the active GPT-5.6 Sol
High state, not a model-verification failure, when `modes.set` successfully
selected both rows and its candidate list contains both labels. Do not block
or fall back to another model in that case.

## Doctor Preflight

Run `doctor({ check: ["bridge", "login", "upload"] })` before long workflows when browser state or permissions are uncertain. Use opt-in checks such as `existing_tab`, `artifacts`, `file_preflight`, `localization`, and `reports` before targeted workflows. The `localization` check verifies registry readiness, not full localized selector coverage. The `file_preflight` check validates supplied local file metadata without opening ChatGPT or attempting upload.

## Attachment Path Rejected

If a Windows-looking path is rejected on macOS/Linux, do not retry with the same string. Convert it to the backend host's real path, for example `/home/you/file.pdf` for a Linux/WSL backend. The backend rejects ambiguous Windows forms such as `C:Users\you\file.pdf`, root-relative paths like `\tmp\file.pdf`, and empty or relative paths.

## File Upload Blocked

Check both permission gates:

1. Chrome `chrome://extensions` > Codex/browser bridge extension > **Details** > **Allow access to file URLs**.
2. Codex settings > **Computer Use > Google Chrome > Permissions > Uploads**.

The SDK should report a structured permission blocker when either gate is missing. Do not retry uploads repeatedly without changing the permission state.
