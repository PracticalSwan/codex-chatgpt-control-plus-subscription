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
- Compose and submit exactly once. A timeout, missing gate, or runtime restart
  is a recovery condition, never permission to resubmit.

## Required Mode

Select GPT-5.6 Sol with High Intelligence before submitting:

```js
const mode = { model: "GPT-5.6 Sol", intelligence: "High" };
```

Inspect the `modes.set` result. It must succeed and report that both the
`GPT-5.6 Sol` model row and the `High` intelligence row were selected. The
current ChatGPT Plus picker may collapse that pair into a single visible
composer control labelled `High` after selection. When the selection result
contains `GPT-5.6 Sol` and `High` is the visible active control, treat that as
verified `GPT-5.6 Sol` at High Intelligence; do not block merely because the
model name is no longer echoed as a second composer button.

The visible picker candidates should include both `GPT-5.6 Sol` and `High` (or
their normalized/localized equivalents). Stop and report the structured
blocker if `modes.set` fails, either requested row cannot be selected, or the
candidate evidence does not contain both parts of the requested mode. Never
substitute another model or intelligence level, and never fall back to Pro.

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

## Completion Envelope

Every focused consultation prompt must require this exact envelope:

```text
<Start>
the complete reply
<End>
```

Append an instruction equivalent to:

> The first non-whitespace characters of your reply must be `<Start>` and the
> final non-whitespace characters must be `<End>`. Emit each marker exactly
> once, put substantive content between them, and do not mention, quote, or
> repeat either marker inside the reply.

Do not include the markers elsewhere in the prompt. Treat a missing, misplaced,
duplicated, or empty envelope as incomplete even when ChatGPT's generation
controls have disappeared and the response text appears stable.

## Submit Once, Then Recover Until Gated

Do not use `runner.run`, `ask`, or `waitAndRead` for a focused consultation.
Use the visible primitives, retain the pre-submit turn baselines, exact claimed
tab, and canonical thread URL when available, and never resubmit after a
timeout.

The following loop uses bounded poll windows, an eight-second recovery delay,
and a fifteen-minute overall recovery budget. The budget prevents a malformed
reply or unavailable session from creating an infinite unattended loop. If the
budget expires, return the exact thread URL and structured blocker; do not
claim to have captured a complete reply.

```js
const START_GATE = "<Start>";
const END_GATE = "<End>";
const COMPLETION_GATE = {
  start: START_GATE,
  end: END_GATE,
  requireUnique: true,
  requireNonEmptyBody: true
};
const POLL_WINDOW = {
  timeoutMs: 45_000,
  stableMs: 2_000,
  pollMs: 750,
  responseContent: "metadata",
  completionGate: COMPLETION_GATE
};
const RECOVERY_DELAY_MS = 8_000;
const RECOVERY_BUDGET_MS = 15 * 60_000;

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const markerCount = (text, marker) => text.split(marker).length - 1;
const isCanonicalThreadUrl = (value) =>
  typeof value === "string"
  && /^https:\/\/chatgpt\.com\/c\/(?!WEB:)[^/?#]+/.test(value);
const validCapture = (text) => {
  const bounded = text.trim();
  return bounded.startsWith(START_GATE)
    && bounded.endsWith(END_GATE)
    && markerCount(bounded, START_GATE) === 1
    && markerCount(bounded, END_GATE) === 1
    && bounded.slice(START_GATE.length, -END_GATE.length).trim().length > 0;
};

const consultation = "Review this plan and recommend improvements:\n\n...";
const prompt = `${consultation}

The first non-whitespace characters of your reply must be <Start> and the final
non-whitespace characters must be <End>. Emit each marker exactly once, put
substantive content between them, and do not mention, quote, or repeat either
marker inside the reply.`;

const boot = await chatgpt.session.bootstrap({ existingTab: true });
const opened = boot.ok ? await chatgpt.threads.new() : boot;
const selected = opened.ok ? await chatgpt.modes.set(mode) : opened;

if (!boot.ok || !opened.ok || !selected.ok) {
  console.log(JSON.stringify({
    status: "blocked_before_submit",
    boot,
    opened,
    selected
  }, null, 2));
} else {
  const afterAssistantTurnCount = selected.context?.assistantTurnCount;
  const afterTurnCount = selected.context?.turnCount;
  const composed = await chatgpt.messages.compose({ text: prompt, mode: "replace" });
  const submitted = composed.ok
    ? await chatgpt.messages.submit({ text: prompt, previousTurnCount: afterTurnCount })
    : composed;
  const recoveryTabId = [
    submitted.context?.tabId,
    selected.context?.tabId,
    boot.data?.tabId,
    boot.context?.tabId
  ].find(value => typeof value === "string" && value.length > 0 && value !== "unknown");
  let threadUrl = isCanonicalThreadUrl(submitted.context?.url)
    ? submitted.context.url
    : undefined;

  if (
    !composed.ok
    || !submitted.ok
    || afterAssistantTurnCount === undefined
    || afterTurnCount === undefined
    || (threadUrl === undefined && recoveryTabId === undefined)
  ) {
    console.log(JSON.stringify({
      status: "submission_or_baseline_unavailable",
      selected,
      composed,
      submitted
    }, null, 2));
  } else {
    const recoveryStartedAt = Date.now();
    let outcome;

    while (Date.now() - recoveryStartedAt < RECOVERY_BUDGET_MS) {
      const wait = await chatgpt.messages.wait({
        ...POLL_WINDOW,
        afterAssistantTurnCount,
        afterTurnCount
      });
      if (isCanonicalThreadUrl(wait.context?.url)) threadUrl = wait.context.url;

      if (wait.data?.completionGate?.status === "complete") {
        const read = await chatgpt.messages.readLatest({
          role: "assistant",
          format: "visible_text"
        });
        if (isCanonicalThreadUrl(read.context?.url)) threadUrl = read.context.url;

        const text = read.data?.text ?? "";
        const advanced = read.ok
          && (read.context?.assistantTurnCount ?? 0) > afterAssistantTurnCount
          && (read.context?.turnCount ?? 0) > afterTurnCount;

        if (advanced && validCapture(text)) {
          outcome = {
            status: "complete",
            threadUrl,
            text: text.trim()
              .slice(START_GATE.length, -END_GATE.length)
              .trim()
          };
          break;
        }
      }

      const hardBlocker = [
        "captcha",
        "login_required",
        "permission",
        "rate_limit",
        "selector_drift"
      ].includes(wait.blocker?.kind);
      if (hardBlocker) {
        outcome = { status: "blocked_during_recovery", threadUrl, recoveryTabId, wait };
        break;
      }

      await sleep(RECOVERY_DELAY_MS);
      if (isCanonicalThreadUrl(threadUrl)) {
        const reopened = await chatgpt.threads.open({ url: threadUrl });
        if (!reopened.ok) {
          outcome = { status: "thread_reopen_failed", threadUrl, recoveryTabId, reopened };
          break;
        }
      }
    }

    console.log(outcome?.status === "complete"
      ? outcome.text
      : JSON.stringify(outcome ?? {
          status: "recovery_budget_exhausted",
          threadUrl,
          recoveryTabId
        }, null, 2));
  }
}
```

Use `visible_text` without `maxChars` for the final gate validation. Markdown
or HTML serialization and caller-supplied clipping can omit the trailing
boundary even when the visible reply contains it.

## Recovery After Browser-Runtime Restart

Persist `threadUrl`, `recoveryTabId`, `afterAssistantTurnCount`, and
`afterTurnCount` outside any single browser-kernel call. `recoveryTabId` is the
exact claimed tab from before submission; it is the only safe bridge across a
runtime failure that happens while the submitted URL is still provisional. If
the browser kernel or automation runtime restarts:

1. Reconnect the browser bridge and reload the packaged runtime.
2. If `threadUrl` is already canonical, bootstrap without creating a new
   thread and open that exact saved URL.
3. If no canonical URL was saved yet, bootstrap against the exact
   `recoveryTabId` with `ifMissing: "block"`. Poll that claimed tab with the
   original baselines until its context has both advanced counts and a
   canonical URL. Save and reopen that URL before continuing.
4. If the exact tab cannot be reclaimed, the URL stays provisional, the counts
   do not advance within the bounded recovery budget, or the claimed tab is no
   longer ChatGPT, return a blocker. Do not search for a similar tab.
5. Resume the same delayed `messages.wait(POLL_WINDOW)` loop with the original
   baselines.
6. Never call `messages.compose` or `messages.submit` during recovery.

```js
let recoveredThreadUrl = isCanonicalThreadUrl(threadUrl) ? threadUrl : undefined;

if (recoveredThreadUrl === undefined) {
  const reclaimed = await chatgpt.session.bootstrap({
    existingTab: {
      target: { type: "tabId", tabId: recoveryTabId },
      ifMissing: "block",
      ifMultiple: "block",
      requireChatGPT: true
    }
  });
  const recoveryStartedAt = Date.now();

  while (reclaimed.ok && Date.now() - recoveryStartedAt < RECOVERY_BUDGET_MS) {
    const probe = await chatgpt.messages.wait({
      ...POLL_WINDOW,
      afterAssistantTurnCount,
      afterTurnCount
    });
    const candidateUrl = probe.context?.url;
    const advanced = (probe.context?.assistantTurnCount ?? 0) > afterAssistantTurnCount
      && (probe.context?.turnCount ?? 0) > afterTurnCount;
    if (advanced && isCanonicalThreadUrl(candidateUrl)) {
      recoveredThreadUrl = candidateUrl;
      break;
    }
    await sleep(RECOVERY_DELAY_MS);
  }
}

if (!isCanonicalThreadUrl(recoveredThreadUrl)) {
  console.log(JSON.stringify({
    status: "exact_thread_recovery_blocked",
    recoveryTabId
  }, null, 2));
} else {
  threadUrl = recoveredThreadUrl;
  const reopened = await chatgpt.threads.open({ url: threadUrl });
  if (!reopened.ok) console.log(JSON.stringify(reopened, null, 2));
}
```

Report a captured answer only when the assistant and total turn counts advanced
past the saved baselines, `messages.wait` reports a complete gate, and the
unclipped `visible_text` independently passes the same exact boundary,
uniqueness, and non-empty-body checks.

## Output Contract

State that the answer came from the visible ChatGPT Plus session with GPT-5.6
Sol at High Intelligence. Include relevant blockers or warnings, and verify
time-sensitive, legal, medical, financial, or other high-stakes claims with
primary sources before presenting them as fact.
