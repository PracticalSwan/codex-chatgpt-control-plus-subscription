import { describe, expect, it } from "vitest";
import { describeCommand } from "../../src/commands/registry.js";

describe("command registry descriptors", () => {
  it("shows the complete demo-safe askWithFiles surface", () => {
    const descriptor = describeCommand("askWithFiles");

    expect(descriptor?.args).toMatchObject({
      files: "absolute local file paths to attach before submitting",
      mode: "optional visible mode selection, e.g. { effort: \"Thinking\" }",
      existingTab: "true or explicit policy to claim a user-open Chrome tab instead of opening a replacement"
    });
    expect(descriptor?.examples.join("\n")).toContain("mode: { effort: \"Thinking\" }");
    expect(descriptor?.examples.join("\n")).toContain("files:");
  });

  it("shows the callable modes.set shape", () => {
    const descriptor = describeCommand("modes.set");

    expect(descriptor?.args).toMatchObject({
      effort: "visible effort label such as Thinking or Extended",
      model: "visible model label such as Instant, Pro, or another available model"
    });
    expect(descriptor?.examples.join("\n")).toContain("chatgpt.modes.set({ effort: \"Thinking\" })");
  });
});
