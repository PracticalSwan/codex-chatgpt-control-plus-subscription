# Troubleshooting

Report structured blockers instead of retrying blindly.

Useful checks:

- `chatgpt.doctor({ check: ["bridge", "login", "upload", "download", "clipboard"] })`
- `chatgpt.help()`
- `chatgpt.commands()`
- `chatgpt.describe("<command-name>")`

Common interpretations:

- `browser_bridge_unavailable`: the process does not have a bridge-enabled `globalThis.agent`.
- `login_required`: the visible ChatGPT session needs user login.
- `captcha`: the user must resolve an interactive challenge.
- `selector_drift`: the ChatGPT UI changed or the selected surface is unsupported.
- `permission`: upload, download, or clipboard permission is missing.
- `rate_limit`: wait or ask the user how to proceed.
- `partial`: a workflow submitted or progressed but did not fully complete.

If a prompt was already submitted and the read timed out, do not resubmit.
Reuse the same visible thread and run another bounded wait/read.

For the focused GPT-5.6 Sol High workflow, preserve both pre-submit turn
baselines, the exact claimed tab id, and the canonical thread URL when
available. Wait eight seconds before reopening that exact thread and polling
again with the same strict `<Start>` / `<End>` completion gate. If the runtime
fails while the URL is still provisional, reclaim only the saved tab and
require advanced counts plus its canonical URL before reopening. Missing,
misplaced, duplicated, empty, or clipped boundaries are incomplete even if the
reply looks stable. Validate an unclipped `visible_text` read only after the
wait reports `completionGate.status === "complete"`.

For generated files, current ChatGPT may expose a filename button that opens an
artifact preview before its Download control appears. Use
`filenamePattern: "^expected\\.csv$"` when the name is known. The plugin handles
that two-step UI and copies path-only Chrome downloads into `destDir`;
`download_filename_not_found` means it intentionally rejected an unrelated
artifact fallback.
