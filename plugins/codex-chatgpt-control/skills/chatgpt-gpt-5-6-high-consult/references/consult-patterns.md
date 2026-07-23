# Consult Patterns

Use GPT-5.6 Sol at High Intelligence through the visible ChatGPT Plus session
for a bounded second opinion, not as independently verified truth.

Good requests name the decision, approved context, exact critique or research
question, known constraints, desired output format, and evidence to verify.
They end with the focused skill's completion-envelope instruction. The rest of
the prompt must not contain `<Start>` or `<End>`, because the runtime requires
each boundary exactly once in the assistant reply.

For a long answer, submit once and retain the canonical thread URL plus both
pre-submit turn baselines. Poll compact metadata with the strict completion
gate. A stable partial reply or absent generation button is not completion
until the trailing gate arrives.

The immediate post-submit URL can contain a provisional `/c/WEB:...`
identifier. Do not reopen that value. Keep polling the claimed page until the
context exposes a canonical `https://chatgpt.com/c/<conversation-id>` URL, then
persist that exact URL for recovery. Also persist the exact claimed tab id at
submission time. If the browser runtime fails before a canonical URL appears,
reclaim only that tab id, require both turn counts to advance past the original
baselines, save its now-canonical URL, and reopen that exact URL. Block instead
of searching for a similar tab when those checks fail.

After an incomplete poll, wait eight seconds before reopening the exact thread
and polling again. After a browser-runtime restart, reconnect, reclaim the saved
tab when necessary, reopen the canonical thread, and resume with the original
baselines. Never duplicate the prompt.
Validate the final unclipped `visible_text`, strip the envelope only after it
passes, and return a blocker instead of a response if the bounded recovery
budget expires.
