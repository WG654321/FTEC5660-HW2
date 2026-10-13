"""Run the unchanged homework CLI serially and retain all attempts as evidence."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default="public_test")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--output", default="experiments/public")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = root / args.output
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for run in range(1, args.runs + 1):
        for attempt in range(1, 4):
            start = time.monotonic()
            try:
                proc = subprocess.run(
                    [sys.executable, "-X", "utf8", "hw2.py", "--cv-folder", args.folder],
                    cwd=root, capture_output=True, text=True, encoding="utf8",
                    env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=1750,
                )
                code, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
            except subprocess.TimeoutExpired:
                code, stdout, stderr = 124, "", "Evaluation subprocess exceeded 1750 seconds."
            prefix = f"run{run}_attempt{attempt}"
            (output / f"{prefix}.log").write_text(stdout + "\n" + stderr, encoding="utf8")
            record = {"run": run, "attempt": attempt, "exit_code": code,
                      "seconds": round(time.monotonic() - start, 2),
                      "source_sha256": hashlib.sha256((root / "hw2.py").read_bytes()).hexdigest()}
            if code == 0 and (root / "results.csv").exists():
                result_bytes = (root / "results.csv").read_bytes()
                (output / f"{prefix}.csv").write_bytes(result_bytes)
                with (root / "results.csv").open(encoding="utf8", newline="") as handle:
                    rows = list(csv.DictReader(handle))
                record["results"] = rows
                record["correct"] = sum(row["correctness"] == "correct" for row in rows)
                record["total"] = len(rows)
            records.append(record)
            (output / "summary.json").write_text(json.dumps(records, indent=2), encoding="utf8")
            print(json.dumps(record), flush=True)
            if code == 0:
                break
            # Preserve bootstrap network failures; do not silently replace their evidence.
            if attempt == 3:
                return 1
            time.sleep(2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
