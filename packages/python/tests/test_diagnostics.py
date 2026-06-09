import json
import unittest
from pathlib import Path

from codex_chatgpt_control import ChatGPT, CommandResult, explain_blocker


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "node" / "contracts" / "v1"
CONTEXT = {
    "timestamp": "2026-06-09T00:00:00.000Z",
    "url": "https://chatgpt.com/c/abc-123",
    "conversationId": "abc-123",
    "tabId": "tab-1",
}


class DiagnosticsTests(unittest.TestCase):
    def test_explain_blocker_accepts_command_result_and_client_method(self) -> None:
        result = CommandResult.from_wire({
            "ok": False,
            "status": "blocked",
            "warnings": [],
            "context": CONTEXT,
            "blocker": {
                "kind": "login_required",
                "message": "ChatGPT login is required before this command can continue.",
            },
        })

        direct = explain_blocker(result, command="session.bootstrap")
        via_client = ChatGPT().explain_blocker(result, command="session.bootstrap")

        self.assertEqual(via_client, direct)
        self.assertEqual(direct["kind"], "login_required")
        self.assertEqual(direct["category"], "auth")
        self.assertTrue(direct["userActionRequired"])
        self.assertFalse(direct["resume"]["supported"])
        self.assertIn("Login required", direct["markdown"])

    def test_matches_shared_blocker_explanation_profile_fixture(self) -> None:
        fixture = json.loads(
            (CONTRACT / "fixtures" / "blocker-explanation-profiles.json").read_text(encoding="utf-8")
        )

        for profile in fixture["result"]["profiles"]:
            with self.subTest(kind=profile["kind"]):
                explanation = explain_blocker({
                    "kind": profile["kind"],
                    "message": f"Blocked by {profile['kind']}.",
                }, command="messages.ask")

                self.assertEqual(explanation["kind"], profile["kind"])
                self.assertEqual(explanation["title"], profile["title"])
                self.assertEqual(explanation["category"], profile["category"])
                self.assertEqual(explanation["severity"], profile["severity"])
                self.assertEqual(explanation["userActionRequired"], profile["userActionRequired"])

    def test_preserves_remediation_candidates_and_existing_tab_metadata_only(self) -> None:
        explanation = explain_blocker({
            "kind": "not_found",
            "code": "existing_tab_not_found",
            "message": "No already-open ChatGPT tab matched the requested existing-tab target.",
            "visibleText": "PRIVATE CHAT CONTENT SHOULD NOT RENDER",
            "remediation": [
                {
                    "label": "Choose an exact tab",
                    "instruction": "Use a ChatGPT conversation URL, conversation ID, or tab id.",
                    "userActionRequired": False,
                }
            ],
            "candidates": [
                {"label": "tab other - Other Chat - https://chatgpt.com/c/other"}
            ],
            "diagnostics": {
                "existingTab": {
                    "requestedTarget": {
                        "type": "conversationId",
                        "conversationId": "abc-123",
                    },
                    "userOpenTabsAvailable": True,
                    "chatgptTabCount": 1,
                    "mismatchReason": "conversation_id_mismatch",
                    "candidateTabs": [
                        {
                            "id": "other",
                            "url": "https://chatgpt.com/c/other",
                            "title": "Other Chat",
                            "conversationId": "other",
                        }
                    ],
                }
            },
        }, command="session.bootstrap")

        self.assertEqual(explanation["category"], "targeting")
        self.assertEqual(explanation["remediation"][0]["label"], "Choose an exact tab")
        self.assertEqual(explanation["candidates"][0]["label"], "tab other - Other Chat - https://chatgpt.com/c/other")
        self.assertEqual(explanation["diagnostics"]["existingTab"]["candidateTabs"][0]["conversationId"], "other")
        self.assertIn("https://chatgpt.com/c/other", explanation["markdown"])
        self.assertNotIn("PRIVATE CHAT CONTENT", explanation["markdown"])

    def test_permission_blocker_with_resumable_state_is_conservative_but_resume_supported(self) -> None:
        explanation = explain_blocker({
            "kind": "permission",
            "code": "upload_permission_required",
            "message": "Upload permission required.",
            "remediation": [
                {
                    "label": "Codex Chrome uploads",
                    "instruction": "Enable Uploads for Chrome in Codex settings.",
                    "userActionRequired": True,
                },
                {
                    "label": "Chrome file URLs",
                    "instruction": "Enable Allow access to file URLs for the Codex Chrome extension.",
                    "userActionRequired": True,
                },
            ],
            "resumable": True,
        }, command="files.attach", state_id="interruption-1")

        self.assertEqual(
            [step["label"] for step in explanation["remediation"]],
            ["Codex Chrome uploads", "Chrome file URLs"],
        )
        self.assertEqual(explanation["resume"], {
            "supported": True,
            "stateId": "interruption-1",
            "command": "files.attach",
        })
        self.assertTrue(explanation["retry"]["safe"])


if __name__ == "__main__":
    unittest.main()
