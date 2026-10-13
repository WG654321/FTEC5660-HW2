import contextlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools import evaluate


class EvaluationEvidenceTests(unittest.TestCase):
    def test_timeout_keeps_partial_stdout_and_stderr(self):
        root = Path(__file__).resolve().parents[1]
        (root / ".tmp").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root / ".tmp") as directory:
            timeout = subprocess.TimeoutExpired(
                cmd="hw2.py", timeout=1750, output=b"completed CV before timeout\n",
                stderr=b"partial verification details\n")
            with patch("sys.argv", ["evaluate", "--runs", "1", "--output", directory]), \
                 patch.object(evaluate.subprocess, "run", side_effect=timeout), \
                 patch.object(evaluate.time, "sleep"), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(evaluate.main(), 1)
            log = (Path(directory) / "run1_attempt1.log").read_text(encoding="utf8")
            self.assertIn("completed CV before timeout", log)
            self.assertIn("partial verification details", log)
            self.assertIn("1750", log)


if __name__ == "__main__":
    unittest.main()
