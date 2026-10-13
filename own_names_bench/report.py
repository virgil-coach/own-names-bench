"""Scores every run and writes the results: one JSON file per run and a Markdown report."""

import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from . import BENCH_VERSION
from .data import Bench
from .run import load_texts
from .score import score
from .stats import cluster_ratio_ci, paired_diff, wilson


def _pct(x: float) -> str:
    return "n/a" if x != x else f"{100 * x:.1f}"


def prop(rows: list[dict], key: str) -> dict | None:
    vals = [r[key] for r in rows if key in r]
    if not vals:
        return None
    k, n = int(sum(vals)), len(vals)
    lo, hi = wilson(k, n)
    return {"k": k, "n": n, "rate": k / n, "lo": lo, "hi": hi}


def ratio(rows: list[dict], num: str, den: str, group: str) -> dict | None:
    rs = [r for r in rows if num in r]
    if not rs:
        return None
    p, lo, hi = cluster_ratio_ci([r[num] for r in rs], [r[den] for r in rs], [r[group] for r in rs])
    return {"num": float(sum(r[num] for r in rs)), "den": float(sum(r[den] for r in rs)), "rate": p, "lo": lo, "hi": hi}


def summarize(b: Bench, s: dict, rows: dict[str, dict], meta: dict) -> dict:
    c, ch = s["clips"], s["chapters"]
    out: dict = {"clips": {}, "chapters": {}}
    for v in ("own", "all"):
        if not any(f"{v}_right" in r for r in c["mentions"]):
            continue
        d = {}
        for g in ("invented", "traditional", "all"):
            ms = [r for r in c["mentions"] if g == "all" or r["group"] == g]
            d[g] = {"right": prop(ms, f"{v}_right"), "wrong_name": prop(ms, f"{v}_wrong_name"),
                    "overwritten": prop(ms, f"{v}_overwritten"), "right_untaught": prop(ms, f"{v}_right_untaught")}
        d["name_free_inserted"] = prop(c["name_free"], f"{v}_inserted")
        d["ordinary_wer"] = ratio(c["wer"], f"{v}_errors", "words", "book")
        # how often the spoken name was among the names the system actually received
        sent = []
        for r in c["mentions"]:
            row = rows.get(f"clip/{r['clip']}/{v}")
            if row is not None:
                sent.append({"in": b.entries[r["entry"]]["written"] in set(row.get("sent", []))})
        d["spoken_name_sent"] = prop(sent, "in")
        out["clips"][v] = d
    if any("none_right" in r for r in c["mentions"]):
        out["clips"]["none"] = {
            g: {"right": prop([r for r in c["mentions"] if g == "all" or r["group"] == g], "none_right")} for g in ("invented", "traditional", "all")
        }
        out["clips"]["none"]["name_free_inserted"] = prop(c["name_free"], "none_inserted")
        out["clips"]["none"]["ordinary_wer"] = ratio(c["wer"], "none_errors", "words", "book")
    for cond in ("taught", "untaught", "none"):
        if not any(f"{cond}_wrong_writes" in r for r in ch["chapters"]):
            continue
        ms = ch["mentions"]
        d = {"right": prop(ms if cond != "untaught" else [m for m in ms if not m["untaught"]], f"{cond}_right"),
             "wrong_writes_per_min": ratio(ch["chapters"], f"{cond}_wrong_writes", "minutes", "chapter"),
             "ordinary_wer": ratio(ch["chapters"], f"{cond}_errors", "words", "chapter")}
        if cond == "untaught":
            un = [m for m in ms if m["untaught"]]
            d["overwritten"] = prop(un, "untaught_other")
            d["right_untaught"] = prop(un, "untaught_right")
        out["chapters"][cond] = d
    # speed and cost
    lat = {}
    for task in ("clip", "chapter"):
        rs = [r for pid, r in rows.items() if pid.startswith(task + "/") and "latency_s" in r]
        if rs:
            ls = np.array([r["latency_s"] for r in rs])
            lat[task] = {"passes": len(rs), "p50_s": float(np.percentile(ls, 50)), "p90_s": float(np.percentile(ls, 90)),
                         "rtf": float(ls.sum() / sum(r["audio_s"] for r in rs))}
    out["speed"] = lat
    price = meta.get("price") or {}
    cost: dict = {}
    if price:
        cost = {"usd_per_audio_hour_no_list": price.get("usd_per_audio_hour"), "usd_per_audio_hour_with_list": price.get("usd_per_audio_hour_with_list"),
                "checked": price.get("checked"), "source": price.get("source"), "basis": "list price"}
    elif meta.get("hourly_usd") and "clip" in lat:
        cost = {"usd_per_audio_hour_with_list": meta["hourly_usd"] * lat["clip"]["rtf"], "basis":
                f"measured real-time factor {lat['clip']['rtf']:.3f} x ${meta['hourly_usd']}/h for the machine"}
    else:
        cost = {"basis": "local; real-time factor on the recorded machine", "rtf": lat.get("clip", {}).get("rtf")}
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
    """System A minus system B on the same items."""
    out = {}
    ca, cb = sa["clips"], sb["clips"]
    ia = {r["id"]: r for r in ca["mentions"]}
    ib = {r["id"]: r for r in cb["mentions"]}
    for v in ("own", "all"):
        for key in ("right", "overwritten"):
            k = f"{v}_{key}"
            ids = [i for i in ia if k in ia[i] and i in ib and k in ib[i]]
            if ids:
                out[k] = paired_diff([ia[i][k] for i in ids], [ib[i][k] for i in ids], [1] * len(ids), [ia[i]["book"] for i in ids])
        wa = {r["clip"]: r for r in ca["wer"]}
        wb = {r["clip"]: r for r in cb["wer"]}
        k = f"{v}_errors"
        ids = [i for i in wa if k in wa[i] and k in wb.get(i, {})]
        if ids:
            out[f"{v}_ordinary_wer"] = paired_diff([wa[i][k] for i in ids], [wb[i][k] for i in ids], [wa[i]["words"] for i in ids],
                                                   [wa[i]["book"] for i in ids])
        fa = {r["id"]: r for r in ca["name_free"]}
        fb = {r["id"]: r for r in cb["name_free"]}
        k = f"{v}_inserted"
        ids = [i for i in fa if k in fa[i] and k in fb.get(i, {})]
        if ids:
            out[k] = paired_diff([fa[i][k] for i in ids], [fb[i][k] for i in ids], [1] * len(ids), [fa[i]["book"] for i in ids])
    ma = {(r["chapter"], n): r for n, r in enumerate(sa["chapters"]["mentions"])}
    mb = {(r["chapter"], n): r for n, r in enumerate(sb["chapters"]["mentions"])}
    k = "taught_right"
    ids = [i for i in ma if k in ma[i] and k in mb.get(i, {})]
    if ids:
        out["chapter_taught_right"] = paired_diff([ma[i][k] for i in ids], [mb[i][k] for i in ids], [1] * len(ids), [i[0] for i in ids])
    return out


def build(b: Bench, runs: list[Path], out_dir: Path, baseline: str | None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for rd in runs:
        meta, rows = load_texts(rd)
        texts = {pid: r["text"] for pid, r in rows.items()}
        s = score(b, texts)
        summary = summarize(b, s, rows, meta)
        label = rd.name
        record = {"label": label, "benchmark_version": BENCH_VERSION, "run": meta, "summary": summary, "items": s,
                  "scored": datetime.now(UTC).isoformat(timespec="seconds")}
        (out_dir / f"{label}.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n")
        results[label] = {"meta": meta, "summary": summary, "items": s}
    md = render(results, baseline)
    path = out_dir / "REPORT.md"
    path.write_text(md)
    return path


def render(results: dict, baseline: str | None) -> str:
    L = [f"# own-names-bench v{BENCH_VERSION} results", "",
         f"Scored {datetime.now(UTC).date().isoformat()}. Percentages with 95% intervals: Wilson for shares of items; bootstrap over books "
         "(clips) or chapters for word error and wrong writes per minute. Every system got the same names in the same order "
         "through its own custom-vocabulary feature; `list fit` says how each fitted them to its limits.", ""]
    for v, title in (("own", "Clips, the book's own name list"), ("all", "Clips, all-books list (902 names)")):
        L += [f"## {title}", "",
              "| System | Names right, invented | Names right, traditional | Names right, all | Untaught overwritten | Wrong name written | "
              "Name-free: a listed name inserted | Ordinary-word error | Spoken name among the names sent |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for label, r in results.items():
            d = r["summary"]["clips"].get(v)
            if not d:
                L.append(f"| {label} | n/a | n/a | n/a | n/a | n/a | n/a | n/a | its feature cannot take this list |")
                continue
            sn = d.get("spoken_name_sent")
            fit = f"{100 * sn['rate']:.1f}%" if sn else "n/a"
            L.append(f"| {label} | {fmt_p(d['invented']['right'])} | {fmt_p(d['traditional']['right'])} | {fmt_p(d['all']['right'])} | "
                     f"{fmt_p(d['all']['overwritten'])} | {fmt_p(d['all']['wrong_name'])} | {fmt_p(d['name_free_inserted'])} | "
                     f"{fmt_r(d['ordinary_wer'])} | {fit} |")
        L.append("")
    L += ["## Clips, no list", "", "| System | Names right, invented | Names right, traditional | Names right, all | Name-free: a book name inserted | Ordinary-word error |",
          "| --- | --- | --- | --- | --- | --- |"]
    for label, r in results.items():
        d = r["summary"]["clips"].get("none")
        if d:
            L.append(f"| {label} | {fmt_p(d['invented']['right'])} | {fmt_p(d['traditional']['right'])} | {fmt_p(d['all']['right'])} | "
                     f"{fmt_p(d['name_free_inserted'])} | {fmt_r(d['ordinary_wer'])} |")
    L += ["", "## Continuous chapters", "",
          "| System | Names right (taught) | Wrong names per minute (taught) | Untaught overwritten | Ordinary-word error (taught) | Names right, no list | Ordinary-word error, no list |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
    for label, r in results.items():
        c = r["summary"]["chapters"]
        t, u, n = c.get("taught"), c.get("untaught"), c.get("none")
        L.append(f"| {label} | {fmt_p(t and t['right'])} | {fmt_r(t and t['wrong_writes_per_min'], 1, 2)} | {fmt_p(u and u['overwritten'])} | "
                 f"{fmt_r(t and t['ordinary_wer'])} | {fmt_p(n and n['right'])} | {fmt_r(n and n['ordinary_wer'])} |")
    L += ["", "## Speed and cost", "", "| System | Machine | Clip latency p50 / p90 (s) | Real-time factor (clips) | Chapter latency p50 (s) | Cost per audio hour |",
          "| --- | --- | --- | --- | --- | --- |"]
    for label, r in results.items():
        sp, cost, m = r["summary"]["speed"], r["summary"]["cost"], r["meta"]["machine"]
        mach = m.get("gpu") or m.get("cpu", "")
        cl, chp = sp.get("clip", {}), sp.get("chapter", {})
        if cost.get("basis") == "list price":
            c = f"${cost['usd_per_audio_hour_with_list']:.3f} with list, ${cost['usd_per_audio_hour_no_list']:.3f} without (list price, {cost['checked']})"
        elif "usd_per_audio_hour_with_list" in cost:
            c = f"${cost['usd_per_audio_hour_with_list']:.3f} ({cost['basis']})"
        else:
            c = cost.get("basis", "")
        L.append(f"| {label} | {mach} | {cl.get('p50_s', float('nan')):.2f} / {cl.get('p90_s', float('nan')):.2f} | "
                 f"{cl.get('rtf', float('nan')):.3f} | {chp.get('p50_s', float('nan')):.1f} | {c} |")
    if baseline and baseline in results:
        L += ["", f"## Paired differences: {baseline} minus each system, same items", "",
              "Points, 95% bootstrap interval over books (chapters for chapter mentions); McNemar exact p on discordant items.", "",
              "| Comparison | Names right (own list) | Untaught overwritten (own list) | Ordinary-word error (own list) | Name-free inserted (own list) | Chapter names right |",
              "| --- | --- | --- | --- | --- | --- |"]

        def cell(d: dict | None) -> str:
            if not d:
                return "n/a"
            s = f"{100 * d['diff']:+.1f} [{100 * d['lo']:+.1f}, {100 * d['hi']:+.1f}]"
            if "mcnemar_p" in d:
                s += f", p={d['mcnemar_p']:.2g} ({d['only_a']} vs {d['only_b']})"
            return s

        for label, r in results.items():
            if label == baseline:
                continue
            p = paired(results[baseline]["items"], r["items"])
            L.append(f"| {baseline} − {label} | {cell(p.get('own_right'))} | {cell(p.get('own_overwritten'))} | {cell(p.get('own_ordinary_wer'))} | "
                     f"{cell(p.get('own_inserted'))} | {cell(p.get('chapter_taught_right'))} |")
    L += ["", "## How each system took the names", ""]
    for label, r in results.items():
        cfg = r["meta"]["config"]
        L.append(f"- **{label}**: {cfg.get('list_feature', '')}; limits: {cfg.get('limits', 'none')}; fit: {cfg.get('fit', '')}")
    L += ["", "## Runs", ""]
    for label, r in results.items():
        m = r["meta"]
        L.append(f"- **{label}**: `{m['system']}` {json.dumps(m['config'], ensure_ascii=False)}; machine {json.dumps(m['machine'])}; "
                 f"code {m['code_revision']}; dataset {m['dataset']} (manifest sha256 {m['manifest_sha256'][:12]}); "
                 f"commands {[c['argv'] for c in m['commands']]}; started {m['commands'][0]['started']}")
    return "\n".join(L) + "\n"
