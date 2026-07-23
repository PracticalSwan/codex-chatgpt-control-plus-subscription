# Changelog

## 0.5.1-alpha.1

- Merges the upstream 0.5.1 Chat/Work surface, lifecycle, artifact, contract,
  packaging, and live-qualification updates into this fork.
- Adds optional strict response completion gates to `messages.wait`, including
  structured missing, duplicate, empty, invalid, and complete statuses.
- Hardens the focused GPT-5.6 Sol High consultation with exact `<Start>` and
  `<End>` boundaries, delayed same-thread recovery, original turn baselines,
  pre-canonical exact-tab recovery, unclipped visible-text validation, and no
  Pro fallback or resubmission.
- Caches an unchanged incomplete gate result by response length/hash so long
  partial replies cross the browser bridge only after their visible text
  changes.
- Retains stopped-generation labels from disabled or non-button status UI
  while excluding assistant prose from generation-state signals.
- Guards inherited registry and GitHub release jobs to the canonical upstream
  repository so fork tags cannot publish upstream-owned package coordinates.
- Captures long visible and normalized response text directly from the
  semantic message node instead of relying on potentially clipped HTML
  serialization.
- Updates the contract validator's transitive `fast-uri` lock entry to 3.1.4
  so the shipped development tree passes the high-severity dependency audit.
- Fixes current Chat/Work pane switching by selecting the visible
  `Select chat surface` radios while retaining legacy button, menu-item, tab,
  link, and bounded DOM fallbacks.
- Correctly detects the checked Work pane and active Work tasks whose home
  surface radio is no longer visible.
- Expands reusable live qualification to cover explicit Chat/Work round trips,
  strict no-op configuration verification, the complete Work lifecycle,
  Work-backed Runner and Responses calls, artifact enumeration, and safe Chat
  restoration.
- Upgrades all bundled skills and plugin packaging validation, and adds an
  opt-in Work configuration mutation test that restores the original setting.

## 0.5.0-alpha.1

- Adds first-class Chat/Work experience detection and verified surface switching.
- Adds surface-aware `configuration.inspect` and strict `configuration.apply` for Chat intelligence/model controls and Work model/effort/speed axes.
- Adds submit-once Work lifecycle commands for start, status, wait, steering, response capture, and artifact access.
- Adds sanitized legacy Chat, simplified Chat, Work basic, Work advanced, and sidebar false-positive profile fixtures to the shared Node/Python conformance suite.
- Adds sync and async Python parity, recursive snake-case wire conversion, runner/Responses support, and Work artifact aliases.
- Rebrands the plugin promise to ChatGPT Surface Control and adds
  `chatgpt-delegate`; package coordinates and legacy mode APIs remain
  compatible. This fork bundles its Sol High focused consultation in the same
  plugin.

## 0.3.0-alpha.1

- Hardens visible mode selection against thread/sidebar action menus: short mode words such as `Pro` no longer match inside pinned-thread titles, localized thread-action labels and `Pin`/`Unpin` prefixes are rejected, and menu enumeration is scoped to open menu containers.
- Adds `modes.get` for reading the visible mode labels without changing them, plus post-selection verification warnings on `modes.set` when the composer does not visibly reflect the requested mode.
- Rewrites `messages.wait` polling around one combined DOM snapshot per poll with length/hash change detection; the full answer crosses the browser bridge once at completion instead of on every poll.
- Adds a persistent-session mode to the Python `NodeSidecarTransport` (context manager or `open()`/`close()`) so multi-command workflows reuse one backend process.
- Adds Windows and Linux clipboard capture (PowerShell `Get-Clipboard`, `xclip`/`xsel`/`wl-paste`) with the existing DOM fallback.
- Fixes report `createdAt` to honor the injected clock so regenerated contract fixtures are deterministic.

## 0.2.0-alpha.1

- Adds cross-platform Windows and macOS path handling, subprocess gates, and public CI coverage.
- Adds broader localized ChatGPT label detection through the shared locale registry.
- Adds untrusted-output envelopes, integrity sidecars, and expanded diagnostics contracts.

## 0.1.0-alpha.1

- Initial public source preparation for `codex-chatgpt-control`.
- Includes the TypeScript visible-session runtime, backend protocol fixtures, and Python parity client.
- Registry publication is intentionally deferred until package allowlists and install smokes pass.
