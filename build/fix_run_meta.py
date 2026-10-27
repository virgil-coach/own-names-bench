#!/usr/bin/env python3
"""The v1.3.0 corrections to published runs' run.json: never a transcript, never an invented value.

A run finished or split across pods (pod/resume.sh, build/merge_runs.py) kept the top-level fields of the
command that made its folder, while each later command records its own code, machine and dataset in
`commands`. Where the truth is recorded there, the top-level field is corrected and the old value kept in
`metadata_fixes`. Where it is not (code run from a working tree with uncommitted changes, `-dirty`), the run
is marked `stale` with why, and `bench report` leaves it out of every result table.

usage: python build/fix_run_meta.py [results/runs]
"""
import json
import sys
from pathlib import Path

AT = "2026-10-27"
V12 = "virgil-coach/own-names-bench@v1.2.0"
DATASET_WHY = ("every current row is of a v1.2.0 pass (completeness checks each row's list fingerprint against v1.2.0's) and the "
               "dataset fingerprint 1625ef57 is v1.2.0's: the v1.0.0 and v1.1.0 audiobook passes ran on audiobook data that v1.1.0 and "
               "v1.2.0 keep unchanged (CHANGES_v1.1_to_v1.2.md), the corrected and suite passes on v1.2.0 (see commands)")


def dirty(m: dict) -> list[dict]:
    """The commands run from a working tree with uncommitted changes. Commands made before they recorded their own
    revision are unknown, except the only command of a run, whose revision is the run's."""
    one = len(m["commands"]) == 1
    return [c for c in m["commands"] if str(c.get("code_revision") or (m.get("code_revision") if one else "")).endswith("-dirty")]


def fix(run: Path) -> list[str]:
    p = run / "run.json"
    m = json.loads(p.read_text())
    done = []
    fixes = list(m.get("metadata_fixes", []))
    seen = {x["field"] for x in fixes}

    def correct(field: str, now, why: str) -> None:
        if field in seen or m.get(field) == now:
            return
        fixes.append({"field": field, "was": m.get(field), "now": now, "why": why, "at": AT})
        m[field] = now
        done.append(f"{field}: -> {now}")

    if run.name in ("parakeet", "qwen-context", "whisper"):
        correct("dataset", V12, DATASET_WHY)
        correct("benchmark_version", "1.2.0", "the suite passes were made by v1.2.0 code (commands at 26ee0b8 / aa5d8b8); " + DATASET_WHY)
    if run.name == "ours" and "PRO 6000" not in m.get("machines", ""):
        m["machines"] += ("; the audiobook clips and chapters ran on the RTX 4090, the calls, svq, ami and modulate suites on an RTX PRO "
                          "6000 Blackwell at $1.69-1.79/h (commands 5 and 6): the speed and cost rows use audiobook passes only")
        done.append("machines: the suites' PRO 6000")
    if run.name == "parakeet" and "speed_note" not in m:
        m["speed_note"] = ("not for speed or cost claims: the clip latencies are mostly the v1.0.0 command's (labelled parakeet-a100, "
                           "--hourly-usd 1.79), whose machine was not recorded; the machine and $0.89/h shown are the 65-pass v1.1.0 rerun's")
        done.append("speed_note")
    bad = dirty(m)
    if bad and "stale" not in m:
        n = sum(int(c.get("passes_to_do") or 0) for c in bad)
        later = {"deepgram": "deepgram-2026-10-26", "elevenlabs": "elevenlabs-2026-10-26"}.get(run.name)
        m["stale"] = (f"{len(bad)} of its {len(m['commands'])} commands{f' ({n} passes to do)' if n else ''} ran from a working tree with uncommitted "
                      "changes (code revision -dirty), which were not recorded, so its code is not known exactly"
                      + (f"; superseded by {later}" if later else ""))
        done.append("stale")
    if not done:
        return done
    if fixes:
        m["metadata_fixes"] = fixes
    p.write_text(json.dumps(m, indent=1) + "\n")
    return done


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "results/runs")
    for run in sorted(d for d in root.iterdir() if (d / "run.json").exists()):
        for x in fix(run):
            print(f"{run.name}: {x}")


if __name__ == "__main__":
    main()
