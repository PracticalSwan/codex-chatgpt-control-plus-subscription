import unittest

from codex_chatgpt_control import ChatGPT, CommandResult


class RecordingBackend:
    def __init__(self) -> None:
        self.requests: list[tuple[str, dict]] = []

    def request(self, command: str, payload: dict | None = None):
        payload = payload or {}
        self.requests.append((command, payload))
        return {
            "ok": True,
            "status": "ok",
            "data": {"command": command, "payload": payload},
            "warnings": [],
            "context": {"timestamp": "2026-06-06T00:00:00.000Z"},
        }


class WorkflowFacadeTests(unittest.TestCase):
    def test_workflow_methods_map_to_backend_commands(self) -> None:
        backend = RecordingBackend()
        chatgpt = ChatGPT(backend=backend)

        calls = [
            (lambda: chatgpt.ask(prompt="hi"), "ask", {"prompt": "hi"}),
            (lambda: chatgpt.ask_in_thread(thread={"type": "current"}, prompt="hi"), "askInThread", {"thread": {"type": "current"}, "prompt": "hi"}),
            (
                lambda: chatgpt.ask_in_thread(
                    thread={"type": "url", "url": "https://chatgpt.com/c/abc-123"},
                    prompt="hi",
                    existing_tab=True,
                ),
                "askInThread",
                {
                    "thread": {"type": "url", "url": "https://chatgpt.com/c/abc-123"},
                    "prompt": "hi",
                    "existingTab": True,
                },
            ),
            (lambda: chatgpt.ask_with_files(prompt="hi", files=["/tmp/a.txt"]), "askWithFiles", {"prompt": "hi", "files": ["/tmp/a.txt"]}),
            (lambda: chatgpt.ask_and_download(prompt="hi", download={"destDir": "/tmp"}), "askAndDownload", {"prompt": "hi", "download": {"destDir": "/tmp"}}),
            (lambda: chatgpt.run_messages(messages=[{"prompt": "one"}]), "runMessages", {"messages": [{"prompt": "one"}]}),
            (lambda: chatgpt.open_thread({"type": "conversationId", "conversationId": "abc"}), "openThread", {"type": "conversationId", "conversationId": "abc"}),
            (lambda: chatgpt.read_latest(format="markdown"), "readLatest", {"format": "markdown"}),
            (lambda: chatgpt.copy_latest(which="latest"), "copyLatest", {"which": "latest"}),
            (lambda: chatgpt.download_latest(dest_dir="/tmp"), "downloadLatest", {"destDir": "/tmp"}),
            (lambda: chatgpt.run_plan({"name": "two-turn"}), "runPlan", {"name": "two-turn"}),
            (lambda: chatgpt.doctor(check=["bridge"]), "doctor", {"check": ["bridge"]}),
            (lambda: chatgpt.create_report({"ok": True}, dest_dir="/tmp"), "createReport", {"result": {"ok": True}, "args": {"destDir": "/tmp"}}),
        ]

        for call, command, payload in calls:
            with self.subTest(command=command):
                result = call()
                self.assertIsInstance(result, CommandResult)
                self.assertEqual(result.data["command"], command)
                self.assertEqual(backend.requests[-1], (command, payload))


if __name__ == "__main__":
    unittest.main()
