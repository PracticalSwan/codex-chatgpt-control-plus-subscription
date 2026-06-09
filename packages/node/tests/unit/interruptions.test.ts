import { describe, expect, it } from "vitest";
import { interruptionFromCommandResult } from "../../src/runner/interruptions.js";
import type { CommandResult } from "../../src/types.js";

const context = { timestamp: "2026-06-05T00:00:00.000Z" };

describe("interruption mapping", () => {
  it("maps upload permission blockers with both remediation gates", () => {
    const result: CommandResult = {
      ok: false,
      status: "blocked",
      warnings: [],
      context,
      blocker: {
        kind: "permission",
        code: "upload_permission_required",
        message: "Upload permission required.",
        remediation: [
          {
            label: "Codex Chrome uploads",
            instruction: "Codex Settings > Computer Use > Chrome > Permissions > Uploads: set to Always allow, or add chatgpt.com.",
            userActionRequired: true
          },
          {
            label: "Chrome file URLs",
            instruction: "Chrome chrome://extensions > Codex extension > Details: enable Allow access to file URLs.",
            userActionRequired: true
          }
        ],
        resumable: true
      }
    };

    const interruption = interruptionFromCommandResult(result, "files.attach");

    expect(interruption?.type).toBe("permission_required");
    expect(interruption?.command).toBe("files.attach");
    expect(interruption?.resume.supported).toBe(true);
    expect(interruption?.fix?.summary).toContain("Upload permission required.");
    expect(interruption?.fix?.steps.join(" ")).toContain("Allow access to file URLs");
  });

  it("marks captcha, login, and rate limits as non-resumable", () => {
    for (const kind of ["captcha", "login_required", "rate_limit"] as const) {
      const result: CommandResult = {
        ok: false,
        status: "blocked",
        warnings: [],
        context,
        blocker: { kind, message: kind, resumable: true }
      };

      const interruption = interruptionFromCommandResult(result, "messages.wait");

      expect(interruption?.type).toBe(kind === "login_required" ? "login_required" : kind);
      expect(interruption?.resume.supported).toBe(false);
      expect(interruption?.resume.reason).toContain("not safe");
    }
  });

  it("maps timeouts without blockers to timeout interruptions", () => {
    const result: CommandResult = {
      ok: false,
      status: "timeout",
      warnings: [],
      error: { name: "WaitTimeout", message: "No assistant response appeared before the timeout.", recoverable: true },
      context
    };

    const interruption = interruptionFromCommandResult(result, "messages.wait");

    expect(interruption).toMatchObject({
      type: "timeout",
      status: "timeout",
      message: "No assistant response appeared before the timeout.",
      resume: { supported: false }
    });
  });
});
