"""Scores every run and writes the results: one JSON file per run and a Markdown report.

Only complete runs are compared. A run is complete when every pass the benchmark expects of that
system (its list variants, every clip and chapter) has a transcript made from the current pass
definition (same list fingerprint) and none failed. Incomplete runs are listed with their counts
and left out of every result table, so a missing outcome can never quietly shrink a denominator.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from . import BENCH_VERSION
from .data import Bench
from .passes import all_passes
from .run import load_rows
from .score import score
from .stats import cluster_ratio_ci, paired_diff

# list variants per system, for runs made before run.json recorded them
SYSTEM_VARIANTS = {"ours": ("none", "own", "all", "xr"), "ours-mlx": ("none", "own", "all", "xr"),
                   "elevenlabs": ("none", "own", "all"), "deepgram": ("none", "own"), "whisper": ("none", "own"),
                   "parakeet": ("none", "own", "all"), "qwen": ("none",), "qwen-context": ("none", "own", "all")}


def _pct(x: float) -> str:
    return "n/a" if x != x else f"{100 * x:.1f}"


def prop(rows: list[dict], key: str, cluster: str) -> dict | None:
    rs = [r for r in rows if key in r]
    if not rs:
        return None
    k, n = int(sum(r[key] for r in rs)), len(rs)
    p, lo, hi = cluster_ratio_ci([float(r[key]) for r in rs], [1.0] * n, [r[cluster] for r in rs])
    return {"k": k, "n": n, "rate": p, "lo": lo, "hi": hi}


def ratio(rows: list[dict], num: str, den: str, group: str) -> dict | None:
    rs = [r for r in rows if num in r]
    if not rs:
        return None
    p, lo, hi = cluster_ratio_ci([r[num] for r in rs], [r[den] for r in rs], [r[group] for r in rs])
    return {"num": float(sum(r[num] for r in rs)), "den": float(sum(r[den] for r in rs)), "rate": p, "lo": lo, "hi": hi}


def completeness(b: Bench, meta: dict, rows: dict[str, dict], failed: dict[str, dict]) -> dict:
    variants = tuple(meta.get("variants") or SYSTEM_VARIANTS[meta["system"]])
    expected = {p.id: p for p in all_passes(b, variants, True)}
    done = {pid for pid, r in rows.items() if pid in expected and r.get("list_sha") == expected[pid].list_sha}
    stale = [pid for pid, r in rows.items() if pid in expected and r.get("list_sha") != expected[pid].list_sha]
    bad = [pid for pid in failed if pid in expected and pid not in done]
    return {"variants": list(variants), "expected": len(expected), "completed": len(done), "failed": len(bad),
            "stale": len(stale), "missing": len(expected) - len(done), "complete": len(done) == len(expected)}


def effective_cost(meta: dict, rows: dict[str, dict]) -> dict:
    """What the run's own workload costs per hour of audio actually sent, by list price with the
    service's billing rules (ElevenLabs: at least 20 s per request with more than 100 keyterms)."""
    price = meta.get("price") or {}
    if not price:
        return {}
    groups: dict[str, list[float]] = {}
    for pid, r in rows.items():
        parts = pid.split("/")
        g = "chapters" if parts[0] == "chapter" else {"none": "clips, no list", "own": "clips, own list", "own-minus": "clips, own list",
                                                     "all": "clips, all-books list", "all-minus": "clips, all-books list"}.get(parts[2], "other")
        n = len(r.get("sent", []))
        secs = r["audio_s"]
        billed = max(secs, price.get("min_billable_s_over_100_terms", 0)) if n > 100 else secs
        usd = billed / 3600 * (price["usd_per_audio_hour_with_list"] if n else price["usd_per_audio_hour"])
        acc = groups.setdefault(g, [0.0, 0.0])
        acc[0] += usd
        acc[1] += secs
    return {g: {"usd": round(u, 3), "audio_hours": round(s / 3600, 3), "usd_per_audio_hour": round(u / (s / 3600), 3)}
            for g, (u, s) in sorted(groups.items())}


def summarize(b: Bench, s: dict, rows: dict[str, dict], meta: dict) -> dict:
    c, ch = s["clips"], s["chapters"]
    out: dict = {"clips": {}, "chapters": {}}
    for v in ("own", "all"):
        if not any(f"{v}_right" in r for r in c["mentions"]):
            continue
        d = {}
        for g in ("invented", "traditional", "all"):
            ms = [r for r in c["mentions"] if g == "all" or r["group"] == g]
            d[g] = {"right": prop(ms, f"{v}_right", "book"), "wrong_name": prop(ms, f"{v}_wrong_name", "book"),
                    "overwritten": prop(ms, f"{v}_overwritten", "book"), "right_untaught": prop(ms, f"{v}_right_untaught", "book")}
        d["name_free_inserted"] = prop(c["name_free"], f"{v}_inserted", "book")
        d["ordinary_wer"] = ratio(c["wer"], f"{v}_errors", "words", "book")
        d["full_wer"] = ratio(c["wer"], f"{v}_full_errors", "full_words", "book")
        sent = []
        for r in c["mentions"]:
            row = rows.get(f"clip/{r['clip']}/{v}")
            if row is not None:
                sent.append({"in": b.entries[r["entry"]]["written"] in set(row.get("sent", [])), "book": r["book"]})
        d["spoken_name_sent"] = prop(sent, "in", "book")
        out["clips"][v] = d
    if any("none_right" in r for r in c["mentions"]):
        out["clips"]["none"] = {g: {"right": prop([r for r in c["mentions"] if g == "all" or r["group"] == g], "none_right", "book")}
                                for g in ("invented", "traditional", "all")}
        out["clips"]["none"]["name_free_inserted"] = prop(c["name_free"], "none_inserted", "book")
        out["clips"]["none"]["ordinary_wer"] = ratio(c["wer"], "none_errors", "words", "book")
        out["clips"]["none"]["full_wer"] = ratio(c["wer"], "none_full_errors", "full_words", "book")
    xs = [r for r in c["mentions"] if "xr_right" in r]
    if xs:
        out["clips"]["xr"] = {"same_reader_right": prop(xs, "own_right", "book"), "other_reader_right": prop(xs, "xr_right", "book"),
                              "other_reader_wrong_name": prop(xs, "xr_wrong_name", "book")}
    for cond in ("taught", "untaught", "none"):
        if not any(f"{cond}_wrong_writes" in r for r in ch["chapters"]):
            continue
        ms = ch["mentions"]
        taught_ms = ms if cond != "untaught" else [m for m in ms if not m["untaught"]]
        d = {"right": prop(taught_ms, f"{cond}_right", "chapter"),
             "right_same_reader": prop([m for m in taught_ms if m["same_reader"]], f"{cond}_right", "chapter"),
             "right_other_reader": prop([m for m in taught_ms if not m["same_reader"]], f"{cond}_right", "chapter"),
             "wrong_writes_per_min": ratio(ch["chapters"], f"{cond}_wrong_writes", "minutes", "chapter"),
             "ordinary_wer": ratio(ch["chapters"], f"{cond}_errors", "words", "chapter"),
             "full_wer": ratio(ch["chapters"], f"{cond}_full_errors", "full_words", "chapter")}
        if cond == "untaught":
            un = [m for m in ms if m["untaught"]]
            d["overwritten"] = prop(un, "untaught_other", "chapter")
            d["right_untaught"] = prop(un, "untaught_right", "chapter")
        out["chapters"][cond] = d
    lat = {}
    for task in ("clip", "chapter"):
        rs = [r for pid, r in rows.items() if pid.startswith(task + "/") and "latency_s" in r]
        if rs:
            ls = np.array([r["latency_s"] for r in rs])
            lat[task] = {"passes": len(rs), "p50_s": float(np.percentile(ls, 50)), "p90_s": float(np.percentile(ls, 90)),
                         "rtf": float(ls.sum() / sum(r["audio_s"] for r in rs))}
    out["speed"] = lat
    price = meta.get("price") or {}
    if price:
        cost = {"basis": "list price", "usd_per_audio_hour_no_list": price.get("usd_per_audio_hour"),
                "usd_per_audio_hour_with_list": price.get("usd_per_audio_hour_with_list"), "checked": price.get("checked"),
                "source": price.get("source"), "effective": effective_cost(meta, rows)}
    elif meta.get("hourly_usd") and "clip" in lat:
        cost = {"basis": "machine", "usd_per_audio_hour_with_list": meta["hourly_usd"] * lat["clip"]["rtf"],
                "note": f"measured real-time factor {lat['clip']['rtf']:.3f} x ${meta['hourly_usd']}/h for the machine"}
    else:
        cost = {"basis": "local", "note": "real-time factor on the recorded machine only"}
    out["cost"] = cost
    return out


def fmt_p(d: dict | None) -> str:
    if not d:
        return "n/a"
    return f"{_pct(d['rate'])} [{_pct(d['lo'])}, {_pct(d['hi'])}]"


def fmt_r(d: dict | None, scale: float = 100, digits: int = 1) -> str:
    if not d:
        return "n/a"
    return f"{d['rate'] * scale:.{digits}f} [{d['lo'] * scale:.{digits}f}, {d['hi'] * scale:.{digits}f}]"


def paired(sa: dict, sb: dict) -> dict:
    """System A minus system B on the same items, clustered by book (clips) or chapter."""
    out = {}
    ca, cb = sa["clips"], sb["clips"]
    ia = {r["id"]: r for r in ca["mentions"]}
    ib = {r["id"]: r for r in cb["mentions"]}

    def items(key: str, groups: tuple[str, ...] = ("invented", "traditional")) -> list[str]:
        return [i for i in ia if key in ia[i] and key in ib.get(i, {}) and ia[i]["group"] in groups]

    for v in ("own", "all"):
        for key in ("right", "overwritten", "wrong_name"):
            k = f"{v}_{key}"
            for gname, groups in (("", ("invented", "traditional")), ("_invented", ("invented",)), ("_traditional", ("traditional",))):
                ids = items(k, groups)
                if ids:
                    out[k + gname] = paired_diff([ia[i][k] for i in ids], [ib[i][k] for i in ids], [1] * len(ids), [ia[i]["book"] for i in ids])
        wa = {r["clip"]: r for r in ca["wer"]}
        wb = {r["clip"]: r for r in cb["wer"]}
        for k, den, name in ((f"{v}_errors", "words", f"{v}_ordinary_wer"), (f"{v}_full_errors", "full_words", f"{v}_full_wer")):
            ids = [i for i in wa if k in wa[i] and k in wb.get(i, {})]
            if ids:
                out[name] = paired_diff([wa[i][k] for i in ids], [wb[i][k] for i in ids], [wa[i][den] for i in ids], [wa[i]["book"] for i in ids])
        fa = {r["id"]: r for r in ca["name_free"]}
        fb = {r["id"]: r for r in cb["name_free"]}
        k = f"{v}_inserted"
        ids = [i for i in fa if k in fa[i] and k in fb.get(i, {})]
        if ids:
            out[k] = paired_diff([fa[i][k] for i in ids], [fb[i][k] for i in ids], [1] * len(ids), [fa[i]["book"] for i in ids])
    ma = {(r["chapter"], n): r for n, r in enumerate(sa["chapters"]["mentions"])}
    mb = {(r["chapter"], n): r for n, r in enumerate(sb["chapters"]["mentions"])}
    for k, name, keep in (("taught_right", "chapter_taught_right", lambda r: True), ("untaught_other", "chapter_overwritten", lambda r: r["untaught"])):
        ids = [i for i in ma if keep(ma[i]) and k in ma[i] and k in mb.get(i, {})]
        if ids:
            out[name] = paired_diff([ma[i][k] for i in ids], [mb[i][k] for i in ids], [1] * len(ids), [i[0] for i in ids])
    ca2 = {r["chapter"]: r for r in sa["chapters"]["chapters"]}
    cb2 = {r["chapter"]: r for r in sb["chapters"]["chapters"]}
    for k, den, name in (("taught_errors", "words", "chapter_ordinary_wer"), ("taught_full_errors", "full_words", "chapter_full_wer"),
                         ("taught_wrong_writes", "minutes", "chapter_wrong_writes_per_min")):
        ids = [i for i in ca2 if k in ca2[i] and k in cb2.get(i, {})]
        if ids:
            out[name] = paired_diff([ca2[i][k] for i in ids], [cb2[i][k] for i in ids], [ca2[i][den] for i in ids], ids)
    return out


def build(b: Bench, runs: list[Path], out_dir: Path, baseline: str | None, pairs: list[tuple[Path, Path]] | None = None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for rd in runs:
        meta, rows, failed = load_rows(rd)
        lav = rd / "loadavg.log"
        if lav.exists():  # a shared machine: its load during the run, logged once a minute
            ones = [float(line.split("{")[1].split()[0]) for line in lav.read_text().splitlines() if "{" in line]
            if ones:
                meta["load_average_1min"] = {"min": min(ones), "median": float(np.median(ones)), "max": max(ones), "samples": len(ones)}
        comp = completeness(b, meta, rows, failed)
        expected = {p.id: p.list_sha for p in all_passes(b, tuple(comp["variants"]), True)}
        current = {pid: r for pid, r in rows.items() if expected.get(pid) == r.get("list_sha")}
        s = score(b, {pid: r["text"] for pid, r in current.items()})
        summary = summarize(b, s, current, meta)
        label = rd.name
        record = {"label": label, "benchmark_version": BENCH_VERSION, "run": meta, "completeness": comp, "summary": summary, "items": s,
                  "scored": datetime.now(UTC).isoformat(timespec="seconds")}
        (out_dir / f"{label}.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n")
        results[label] = {"meta": meta, "summary": summary, "items": s, "completeness": comp}
    md = render(results, baseline)
    if pairs:
        md += reproducibility(b, pairs, out_dir)
    path = out_dir / "REPORT.md"
    path.write_text(md)
    return path


def _cell(d: dict | None, digits: int = 1) -> str:
    if not d:
        return "n/a"
    s = f"{100 * d['diff']:+.{digits}f} [{100 * d['lo']:+.{digits}f}, {100 * d['hi']:+.{digits}f}]"
    if "only_a" in d:
        s += f" ({d['only_a']} vs {d['only_b']})"
    return s + (" **holds**" if d.get("holds") else "")


def render(results: dict, baseline: str | None) -> str:
    L = [f"# own-names-bench v{BENCH_VERSION} results", "",
         f"Scored {datetime.now(UTC).date().isoformat()}. Rates in percent with 95% intervals from a bootstrap over clusters: books "
         "for clips (each clip book has one reader), chapters for chapters. Name matches are one to one. Every system got the same "
         "names in the same order through its own custom-vocabulary feature.", "",
         "## Runs: expected, completed and failed passes", "",
         "| Run | System | List variants | Expected | Completed | Failed | Stale (made from an older list) | Complete |",
         "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for label, r in results.items():
        c = r["completeness"]
        L.append(f"| {label} | {r['meta']['system']} | {', '.join(c['variants'])} | {c['expected']} | {c['completed']} | {c['failed']} | "
                 f"{c['stale']} | {'yes' if c['complete'] else '**no: left out of every table below**'} |")
    results = {k: v for k, v in results.items() if v["completeness"]["complete"]}
    for v, title in (("own", "Clips, the book's own name list"), ("all", "Clips, all-books list (902 entries)")):
        L += ["", f"## {title}", "",
              "| System | Names right, invented | Names right, traditional | Names right, all | Untaught overwritten | Wrong name written | "
              "Name-free: a listed name inserted | Ordinary-word error | Full-transcript error | Spoken name among the names sent |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for label, r in results.items():
            d = r["summary"]["clips"].get(v)
            if not d:
                L.append(f"| {label} | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |")
                continue
            L.append(f"| {label} | {fmt_p(d['invented']['right'])} | {fmt_p(d['traditional']['right'])} | {fmt_p(d['all']['right'])} | "
                     f"{fmt_p(d['all']['overwritten'])} | {fmt_p(d['all']['wrong_name'])} | {fmt_p(d['name_free_inserted'])} | "
                     f"{fmt_r(d['ordinary_wer'])} | {fmt_r(d['full_wer'])} | {fmt_p(d.get('spoken_name_sent'))} |")
    L += ["", "## Clips, no list", "",
          "| System | Names right, invented | Names right, traditional | Names right, all | Name-free: a book name inserted | Ordinary-word error | Full-transcript error |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
    for label, r in results.items():
        d = r["summary"]["clips"].get("none")
        if d:
            L.append(f"| {label} | {fmt_p(d['invented']['right'])} | {fmt_p(d['traditional']['right'])} | {fmt_p(d['all']['right'])} | "
                     f"{fmt_p(d['name_free_inserted'])} | {fmt_r(d['ordinary_wer'])} | {fmt_r(d['full_wer'])} |")
    L += ["", "## Continuous chapters", "",
          "| System | Names right (taught) | same reader taught it | another reader taught it | Wrong names per minute | Untaught overwritten | "
          "Ordinary-word error | Full-transcript error | Names right, no list |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for label, r in results.items():
        c = r["summary"]["chapters"]
        t, u, n = c.get("taught"), c.get("untaught"), c.get("none")
        L.append(f"| {label} | {fmt_p(t and t['right'])} | {fmt_p(t and t['right_same_reader'])} | {fmt_p(t and t['right_other_reader'])} | "
                 f"{fmt_r(t and t['wrong_writes_per_min'], 1, 2)} | {fmt_p(u and u['overwritten'])} | {fmt_r(t and t['ordinary_wer'])} | "
                 f"{fmt_r(t and t['full_wer'])} | {fmt_p(n and n['right'])} |")
    xr_rows = [(label, r["summary"]["clips"]["xr"]) for label, r in results.items() if "xr" in r["summary"]["clips"]]
    if xr_rows:
        L += ["", "## Taught in the reader's own voice or another reader's (clips)", "",
              "Systems taught by recording. Mentions whose name another benchmark book also lists, read by a different reader: the same "
              "clip and own list, with the name taught once by the clip's reader and once by the other reader.", "",
              "| System | Mentions | Right, taught by the same reader | Right, taught by another reader | Another listed name written instead |",
              "| --- | --- | --- | --- | --- |"]
        for label, x in xr_rows:
            L.append(f"| {label} | {x['other_reader_right']['n']} | {fmt_p(x['same_reader_right'])} | {fmt_p(x['other_reader_right'])} | "
                     f"{fmt_p(x['other_reader_wrong_name'])} |")
    L += ["", "## Speed and cost", "",
          "| System | Machine | Clip latency p50 / p90 (s) | Real-time factor (clips) | Cost per audio hour: nominal | Cost per audio hour: this workload |",
          "| --- | --- | --- | --- | --- | --- |"]
    for label, r in results.items():
        sp, cost, m = r["summary"]["speed"], r["summary"]["cost"], r["meta"]["machine"]
        mach = m.get("gpu") or m.get("cpu", "")
        if r["meta"].get("load_average_1min"):
            la = r["meta"]["load_average_1min"]
            mach += f" (shared; 1-min load {la['min']:.0f}–{la['max']:.0f}, median {la['median']:.0f}: not for latency claims)"
        cl = sp.get("clip", {})
        if cost["basis"] == "list price":
            nominal = f"${cost['usd_per_audio_hour_with_list']:.3f} with a list, ${cost['usd_per_audio_hour_no_list']:.3f} without ({cost['checked']})"
            eff = "; ".join(f"{g} ${e['usd_per_audio_hour']:.3f}" for g, e in cost["effective"].items())
        elif cost["basis"] == "machine":
            nominal, eff = f"${cost['usd_per_audio_hour_with_list']:.3f}", cost["note"]
        else:
            nominal, eff = "n/a", cost["note"]
        L.append(f"| {label} | {mach} | {cl.get('p50_s', float('nan')):.2f} / {cl.get('p90_s', float('nan')):.2f} | "
                 f"{cl.get('rtf', float('nan')):.3f} | {nominal} | {eff} |")
    if baseline and baseline in results:
        L += ["", f"## Paired differences: {baseline} minus each system, same items", "",
              "Points, 95% bootstrap interval over books (clips) or chapters; **holds** when the interval excludes zero. In brackets: "
              "items only the first system / only the second got (no item-level test; it would ignore the clustering).", ""]
        rows_spec = [("Names right, own list", "own_right"), ("  invented", "own_right_invented"), ("  traditional", "own_right_traditional"),
                     ("Untaught overwritten, own list", "own_overwritten"), ("Wrong name written, own list", "own_wrong_name"),
                     ("Name-free inserted, own list", "own_inserted"), ("Ordinary-word error, own list", "own_ordinary_wer"),
                     ("Full-transcript error, own list", "own_full_wer"), ("Names right, all-books list", "all_right"),
                     ("Untaught overwritten, all-books list", "all_overwritten"), ("Chapters: names right", "chapter_taught_right"),
                     ("Chapters: untaught overwritten", "chapter_overwritten"), ("Chapters: ordinary-word error", "chapter_ordinary_wer"),
                     ("Chapters: full-transcript error", "chapter_full_wer")]
        others = [label for label in results if label != baseline]
        L += ["| Measure | " + " | ".join(f"{baseline} − {o}" for o in others) + " |", "| --- |" + " --- |" * len(others)]
        ps = {o: paired(results[baseline]["items"], results[o]["items"]) for o in others}
        for title, key in rows_spec:
            L.append(f"| {title} | " + " | ".join(_cell(ps[o].get(key)) for o in others) + " |")
        wpm = [o for o in others if "chapter_wrong_writes_per_min" in ps[o]]
        if wpm:
            L.append("| Chapters: wrong names per minute | " + " | ".join(
                (lambda d: f"{d['diff']:+.2f} [{d['lo']:+.2f}, {d['hi']:+.2f}]" + (" **holds**" if d["holds"] else ""))(ps[o]["chapter_wrong_writes_per_min"])
                if o in wpm else "n/a" for o in others) + " |")
    L += ["", "## How each system took the names", ""]
    for label, r in results.items():
        cfg = r["meta"]["config"]
        L.append(f"- **{label}**: {cfg.get('list_feature', '')}; limits: {cfg.get('limits', 'none')}; fit: {cfg.get('fit', '')}")
    L += ["", "## Runs", ""]
    for label, r in results.items():
        m = r["meta"]
        L.append(f"- **{label}**: `{m['system']}` {json.dumps(m['config'], ensure_ascii=False)}; machine {json.dumps(m['machine'])}; "
                 f"code {m['code_revision']}; dataset {m['dataset']} (fingerprint {m.get('dataset_fingerprint', '')[:12]}); "
                 f"commands {[c['argv'] for c in m['commands']]}; started {m['commands'][0]['started']}"
                 + (f"; note: {m['note']}" if m.get("note") else ""))
    return "\n".join(L) + "\n"


def reproducibility(b: Bench, pairs: list[tuple[Path, Path]], out_dir: Path) -> str:
    """The same system run on two machines (or two runtimes), pass by pass and item by item."""
    from .compare import compare

    L = ["", "## Reproducibility: the same system on two machines", "",
         "Identical text: passes whose transcript is the same string. Word difference: word error of one run's text against "
         "the other's. Paired difference: first minus second, same items, 95% bootstrap interval over books.", "",
         "| Runs | Machines | Passes | Identical text | Word difference | Same shortlist (windows) | Items with the same outcome: right (own list) / overwritten | "
         "Names right (own list), difference | Untaught overwritten, difference | Chapter names right, difference |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    records = []
    for a, c in pairs:
        r = compare(b, a, c)
        records.append(r)
        ma, mb = r["a"]["machine"], r["b"]["machine"]
        mach = f"{ma.get('gpu') or ma.get('cpu')} vs {mb.get('gpu') or mb.get('cpu')}"
        sl = r["windows_same_shortlist"]
        slt = f"{sl['same']}/{sl['of']} ({100 * sl['same'] / sl['of']:.1f}%)" if sl["of"] else "n/a"
        it = r["items"]
        agree = " / ".join(f"{it[k]['agree']}/{it[k]['items']}" for k in ("own_right", "own_overwritten") if k in it)
        p = r["paired_a_minus_b"]
        L.append(f"| {r['a']['label']} vs {r['b']['label']} | {mach} | {r['passes_compared']} | "
                 f"{r['identical_text']} ({100 * r['identical_text'] / max(1, r['passes_compared']):.1f}%) | "
                 f"{100 * r['word_difference_between_runs']:.2f}% | {slt} | {agree} | {_cell(p.get('own_right'), 2)} | "
                 f"{_cell(p.get('own_overwritten'), 2)} | {_cell(p.get('chapter_taught_right'), 2)} |")
    (out_dir / "reproducibility.json").write_text(json.dumps(records, indent=1) + "\n")
    return "\n".join(L) + "\n"
