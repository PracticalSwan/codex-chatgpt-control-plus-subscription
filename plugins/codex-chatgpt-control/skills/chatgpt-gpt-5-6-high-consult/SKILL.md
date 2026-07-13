---
name: chatgpt-gpt-5-6-high-consult
description: Use when Codex should consult the user's visible ChatGPT Plus web session with GPT-5.6 Sol at High Intelligence for planning, research, review, critique, or a second opinion through the codex-chatgpt-control plugin.
---

# ChatGPT GPT-5.6 Sol High Intelligence Consult

Use this focused workflow for deep planning, research, logical reasoning,
reviews, naming, positioning, brainstorming, design critique, and second
opinions. It is a visible, user-directed ChatGPT web workflow, not an OpenAI
API client or a background browser automation service.

This focused skill is bundled with the broad control skill in the single
`codex-chatgpt-control` plugin. Do not install or package it separately.

Use the broad `codex-chatgpt-control` skill first when bridge bootstrap, file
attachment, tab handling, download permissions, or selector diagnosis is the
main issue.

## Guardrails

- Send only user-approved, non-sensitive prompt and attachment content.
- Use only visible ChatGPT web through the Codex/browser bridge. Do not call
  private endpoints or inspect cookies, local storage, or hidden credentials.
- Prefer a fresh thread unless the user identified a specific existing one.
- Keep reports redacted by default and treat the answer as model judgment, not
  independently verified fact.
- Do not select or fall back to Pro.

## Required Mode

Select GPT-5.6 Sol with High Intelligence before submitting:

```js
const mode = { model: "GPT-5.6 Sol", intelligence: "High" };
```

Inspect the `modes.set` result. If the model or High cannot be selected, stop
and report its structured blocker and visible candidates; do not substitute a
different model or intelligence level.

If duplicate exact `GPT-5.6 Sol` labels make the model unaddressable and the
user explicitly confirmed that the visible ChatGPT tab is already set to
GPT-5.6 Sol, preserve that model and set only:

```js
const mode = { intelligence: "High" };
```

Report that this is a user-confirmed model selection rather than an independent
SDK read.

## Runtime Loader

Resolve the packaged runtime from this skill directory:

```text
../../runtime/import-chatgpt-control.mjs
```

```js
const loaderUrl = new URL(
  "../../runtime/import-chatgpt-control.mjs",
  import.meta.url,
);
const { importChatGPTControl } = await import(loaderUrl.href);
const { createChatGPT } = await importChatGPTControl();
const chatgpt = createChatGPT({ agent: globalThis.agent });
```

Use these runtime primitives rather than duplicating browser automation.

## Submit Once, Then Poll

Do not use `runner.run`, `ask`, or `waitAndRead` for a focused consultation.
Use the visible primitives, retain the pre-submit turn baselines and thread URL,
and never resubmit after any timeout.

```js
const POLL_WINDOW = {
  timeoutMs: 45_000,
  stableMs: 2_000,
  pollMs: 750,
  responseContent: "metadata"
};

const boot = await chatgpt.session.bootstrap({ existingTab: true });
const opened = boot.ok ? await chatgpt.threads.new() : boot;
const selected = opened.ok ? await chatgpt.modes.set(mode) : opened;

if (!boot.ok || !opened.ok || !selected.ok) {
  console.log(JSON.stringify({ status: "blocked_before_submit", boot, opened, selected }, null, 2));
} else {
  const afterAssistantTurnCount = selected.context?.assistantTurnCount;
  const afterTurnCount = selected.context?.turnCount;
  const prompt = "Review this plan and recommend improvements:\n\n...";
  const composed = await chatgpt.messages.compose({ text: prompt, mode: "replace" });
  const submitted = composed.ok
    ? await chatgpt.messages.submit({ text: prompt, previousTurnCount: afterTurnCount })
    : composed;
  let threadUrl = submitted.context?.url;

  if (!composed.ok || !submitted.ok || afterAssistantTurnCount === undefined || afterTurnCount === undefined) {
    console.log(JSON.stringify({ status: "submission_or_baseline_unavailable", selected, composed, submitted }, null, 2));
  } else {
    const wait = await chatgpt.messages.wait({
      ...POLL_WINDOW,
      afterAssistantTurnCount,
      afterTurnCount
    });
    if (wait.context?.url?.includes("/c/")) threadUrl = wait.context.url;

    const read = await chatgpt.messages.readLatest({ role: "assistant", format: "markdown" });
    if (read.context?.url?.includes("/c/")) threadUrl = read.context.url;
    const captured = read.ok
      && (read.context?.assistantTurnCount ?? 0) > afterAssistantTurnCount
      && (read.context?.turnCount ?? 0) > afterTurnCount;

    console.log(captured
      ? read.data?.text ?? ""
      : JSON.stringify({ status: wait.ok ? "capture_unavailable" : wait.status, threadUrl, wait, read }, null, 2));
  }
}
```

## Recovery After Poll Or Browser-Runtime Timeout

- Preserve the submitted `threadUrl`, `afterAssistantTurnCount`, and
  `afterTurnCount`; do not trust whichever ChatGPT tab happens to be active.
- In the same runtime, run another bounded `messages.wait(POLL_WINDOW)` and
  `messages.readLatest(...)` against the same thread. Do not compose or submit
  again.
- If the browser kernel or automation runtime restarted, bootstrap it, reopen
  the exact submitted thread, and reuse the original baselines:

  ```js
  await chatgpt.session.bootstrap({ existingTab: true });
  const opened = await chatgpt.threads.open({ url: threadUrl });
  if (!opened.ok) console.log(JSON.stringify(opened, null, 2));
  ```

- Report a captured answer only when `read.ok` is true and both total and
  assistant turn counts advanced past the saved baselines. Otherwise report the
  structured wait/read result and thread URL without claiming success.

## Output Contract

State that the answer came from the visible ChatGPT Plus session with GPT-5.6
Sol at High Intelligence. Include relevant blockers or warnings, and verify
time-sensitive, legal, medical, financial, or other high-stakes claims with
primary sources before presenting them as fact.
