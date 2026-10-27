#!/usr/bin/env python3
"""Checks the sealed v1.3 results from a clone and the v1.3.0 dataset: each sealed suite's files against its suite hash,
each published pass output against the SHA-256 recorded when it was scored (results/<suite>/SHA256SUMS.passes), and each
report rebuilt by `bench report` from those passes against the committed one: every result table of REPORT.md and every
run's summary and completeness in scores/summary.json. Prints aggregates only, as the report does.

The committed reports were made by the code of the time (benchmark 1.2.0 code, on the same data format); a rebuild with this
code differs only in the title, the scoring date and the runs list, which are left out of the comparison.

usage: uv run python scripts/verify_sealed.py DATASET [books13 conv13]
"""

import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from own_names_bench.data import check_sealed

ROOT = Path(__file__).resolve().parent.parent
BASELINE = {"books13": "books13-v7c-mlx", "conv13": "conv13-v7c-mlx"}


def tables(md: str) -> list[str]:
    out, section = [], ""
    for line in md.splitlines():
        if line.startswith("## "):
            section = line
        elif line.startswith("|") and section != "## Runs":
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) > 2 and all(c == "n/a" for c in cells[1:-1]):  # a row with no numbers: its note's wording changed in 1.3.0
                cells[-1] = "n/a"
            out.append(f"{section} | " + " | ".join(cells) + " |")
    return out


def main() -> None:
    data = Path(sys.argv[1]).resolve()
    suites = sys.argv[2:] or list(BASELINE)
    hashes = check_sealed(data)
    ok = True
    for suite in suites:
        print(f"== {suite}: suite hash {hashes[suite]}")
        res = ROOT / "results" / suite
        sums = dict(line.split("  ", 1)[::-1] for line in (res / "SHA256SUMS.passes").read_text().splitlines())
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp) / "runs"
            for rel, want in sums.items():
                if not rel.endswith("/passes.jsonl"):
                    continue
                raw = gzip.decompress((res / (rel + ".gz")).read_bytes())
                got = hashlib.sha256(raw).hexdigest()
                print(f"{rel}: {'matches' if got == want else 'DIFFERS FROM'} the sha256 recorded when it was scored")
                ok &= got == want
                d = runs / rel.split("/")[0]
                d.mkdir(parents=True)
                (d / "passes.jsonl.gz").write_bytes(gzip.compress(raw, mtime=0))
                for f in ("run.json", "loadavg.log"):
                    if (res / d.name / f).exists():
                        (d / f).write_bytes((res / d.name / f).read_bytes())
            out = Path(tmp) / "scores"
            subprocess.run(["bench", "--data", str(data / suite), "report", "--runs", str(runs), "--out", str(out),
                            "--baseline", BASELINE[suite]], check=True, stdout=subprocess.DEVNULL)
            committed = json.loads((res / "scores" / "summary.json").read_text())
            for label, rec in committed.items():
                new = json.loads((out / f"{label}.json").read_text())
                same = new["summary"] == rec["summary"] and new["completeness"] == {**rec["completeness"], "chapters": True}
                print(f"{label}: summary and completeness {'reproduced' if same else 'DIFFER'}")
                ok &= same
            a, b = tables((res / "scores" / "REPORT.md").read_text()), tables((out / "REPORT.md").read_text())
            print(f"REPORT.md: {len(a)} table rows, {'reproduced' if a == b else 'DIFFER'}")
            ok &= a == b
    print("SEALED RESULTS VERIFIED" if ok else "SEALED RESULTS DO NOT VERIFY")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
