# Changelog

## 0.3.0-alpha.2

- Replaces the focused Pro consultation skill with
  `chatgpt-gpt-5-6-high-consult`, targeting visible ChatGPT Plus sessions with
  GPT-5.6 Sol at High Intelligence and no Pro fallback.
- Documents primitive-only submission, bounded metadata polling, and exact
  thread recovery after polling or browser-runtime timeouts without prompt
  resubmission.
- Prevents assistant prose containing stop/cancel words from being interpreted
  as a live generation control, and skips timed-out single-flight snapshot
  polls without resetting response stability.
- Makes plugin runtime builds work from Windows by invoking `npm.cmd`.

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
