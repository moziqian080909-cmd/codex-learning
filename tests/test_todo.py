import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "todo.py"


class TodoTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "nested" / "tasks.json"

    def run_cli(self, *arguments, code=0):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--file", str(self.path), *arguments],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, code, result.stderr)
        return result

    def test_persistent_workflow(self):
        self.assertIn("暂无任务", self.run_cli("list").stdout)
        self.run_cli("add", "学习 Python")
        self.run_cli("add", "完成练习")
        self.assertIn("1. [ ] 学习 Python", self.run_cli("list").stdout)
        self.run_cli("done", "1")
        self.run_cli("done", "1")
        output = self.run_cli("list").stdout
        self.assertIn("1. [x] 学习 Python", output)
        self.assertIn("2. [ ] 完成练习", output)
        self.assertEqual(len(json.loads(self.path.read_text())), 2)

    def test_invalid_input_preserves_data(self):
        self.run_cli("add", "有效任务")
        before = self.path.read_bytes()
        self.assertIn("不能为空", self.run_cli("add", "  ", code=1).stderr)
        self.assertIn("找不到", self.run_cli("done", "99", code=1).stderr)
        self.run_cli("done", "abc", code=2)
        self.assertEqual(self.path.read_bytes(), before)

    def test_corrupt_data_is_not_overwritten(self):
        self.path.parent.mkdir()
        for contents in ['{broken', '{}', '[{"id": true}]']:
            with self.subTest(contents=contents):
                self.path.write_text(contents)
                self.assertIn("错误", self.run_cli("add", "任务", code=1).stderr)
                self.assertEqual(self.path.read_text(), contents)

    def test_filesystem_error(self):
        self.path.mkdir(parents=True)
        self.assertIn("错误", self.run_cli("list", code=1).stderr)


if __name__ == "__main__":
    unittest.main()
