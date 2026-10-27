"""Scoring checks on the real dataset: the reference scores perfectly, an empty answer scores
nothing, and writing another listed name over a mention is caught. Needs the dataset
(OWN_NAMES_BENCH_DATA or ./data)."""

import pytest

from own_names_bench.align import GAP, align
from own_names_bench.data import default_dir, load
from own_names_bench.passes import all_passes
from own_names_bench.report import summarize
from own_names_bench.text import name_tokens, ordinary_tokens


def test_align_gap_absorbs_words():
    a = align([GAP, "a", "b", GAP], ["x", "y", "a", "b", "z"])
    assert a.errors == 0 and a.ref_words == 2
    assert a.in_gap == [True, True, False, False, True]


def test_align_counts_errors():
    a = align(["a", "b", "c"], ["a", "x", "c", "d"])
    assert a.errors == 2


def test_name_tokens():
    assert name_tokens("Mana-Yood-Sushai's tower") == ["mana", "yood", "sushai", "tower"]
    assert name_tokens("Carcë") != name_tokens("Carce")
    assert ordinary_tokens("Colour, twenty-one!") == ["color", "21"]
    assert ordinary_tokens("(A privilege) lopp'd o'er th' sea; he'd") == ["a", "privilege", "lopped", "over", "the", "sea", "he", "would"]


@pytest.fixture(scope="module")
def bench():
    root = default_dir()
    if not (root / "manifest.json").exists():
        pytest.skip("dataset not present")
    return load(root, verify=False)


def _reference_texts(b):
    from own_names_bench.passes import view

    texts = {}
    for p in all_passes(b, ("none", "own", "all"), True):
        if p.task == "clip":
            parts = p.id.split("/")
            clip = parts[parts.index("clip") + 1]
            texts[p.id] = view(b, p).clips[clip]["reference"]
        else:
            ch = next(c for c in b.m["chapters"] if c["id"] == p.id.split("/")[1])
            texts[p.id] = " ".join(s["reference"] for s in ch["segments"])
    return texts


def test_reference_is_perfect(bench):
    from own_names_bench.score import score

    s = score(bench, _reference_texts(bench))
    rows = {k: {"latency_s": 0.0, "audio_s": 1.0} for k in []}
    sm = summarize(bench, s, rows, {})
    for v in ("own", "all"):
        assert sm["clips"][v]["all"]["right"]["rate"] == 1.0
        assert sm["clips"][v]["all"]["overwritten"]["rate"] == 0.0
        assert sm["clips"][v]["all"]["wrong_name"]["rate"] == 0.0
        assert sm["clips"][v]["name_free_inserted"]["rate"] == 0.0
        assert sm["clips"][v]["ordinary_wer"]["rate"] == 0.0
    assert sm["chapters"]["taught"]["right"]["rate"] == 1.0
    assert sm["chapters"]["taught"]["wrong_writes_per_min"]["rate"] == 0.0
    assert sm["chapters"]["taught"]["ordinary_wer"]["rate"] < 1e-3  # numbers normalized across segment joins
    for name, x in sm["suites"].items():
        if "right" in x:
            assert x["right"]["rate"] == 1.0 and x["overwritten"]["rate"] == 0.0, name
        if "own_free_inserted" in x:
            assert x["own_free_inserted"]["rate"] == 0.0, name


def test_empty_answer_scores_nothing(bench):
    from own_names_bench.score import score

    s = score(bench, {k: "" for k in _reference_texts(bench)})
    sm = summarize(bench, s, {}, {})
    assert sm["clips"]["own"]["all"]["right"]["rate"] == 0.0
    assert sm["clips"]["own"]["ordinary_wer"]["rate"] == 1.0


def test_overwrite_is_caught(bench):
    from own_names_bench.score import score

    texts = _reference_texts(bench)
    mn = bench.m["mentions"][0]
    clip = bench.clips[mn["clip"]]
    book = clip["book"]
    other = next(e for e in bench.lists[f"own:{book}"]["entries"] if e != mn["entry"])
    a, z = mn["span"]
    swapped = clip["reference"][:a] + bench.entries[other]["written"] + clip["reference"][z:]
    texts[f"clip/{mn['clip']}/own-minus/{mn['entry']}"] = swapped
    s = score(bench, texts)
    row = next(r for r in s["clips"]["mentions"] if r["id"] == mn["id"])
    assert row["own_overwritten"] is True and row["own_right_untaught"] is False


def test_one_to_one_mentions():
    from own_names_bench.score import Matched

    ref = name_tokens("Alice Alice went home")
    m = Matched(ref, name_tokens("Alice went home"))
    key = ("alice",)
    assert sum(m.right(key, lo) for lo in (0, 1)) == 1
    m2 = Matched(ref, name_tokens("Alice Alice went home"))
    assert m2.right(key, 0) and m2.right(key, 1)


def test_unclaimed_listed_name_counts_once():
    from own_names_bench.score import Matched

    # "Bob" really is said next to the mention: writing it is not an overwrite of Alice
    m = Matched(name_tokens("Alice and Bob went"), name_tokens("Bob and Bob went"))
    assert not m.right(("alice",), 0)
    assert m.unclaimed_at(("bob",), 0, 1)  # the first Bob stands where Alice was said and no reference Bob claims it
    m2 = Matched(name_tokens("Alice and Bob went"), name_tokens("Alice and Bob went"))
    assert not m2.unclaimed_at(("bob",), 0, 1)


def test_untaught_list_drops_every_same_spelling(bench):
    from own_names_bench.passes import minus
    from own_names_bench.text import name_key

    for mn in bench.m["mentions"]:
        book = bench.clips[mn["clip"]]["book"]
        key = name_key(bench.entries[mn["entry"]]["written"])
        for v in ("own", "all"):
            left = minus(bench, bench.lists[f"{v}:{book}"]["entries"], mn["entry"])
            assert all(name_key(bench.entries[e]["written"]) != key for e in left)


class _Fake:
    name = "fake"
    kind = "local"
    variants = ("none",)
    workers = 1

    def __init__(self, setting: str = "a") -> None:
        self.setting = setting

    def config(self) -> dict:
        return {"setting": self.setting}

    def price(self) -> dict:
        return {}

    def fit(self, names):
        from own_names_bench.systems.base import Fit

        return Fit(list(names))


def test_resume_refuses_another_system_or_config(bench, tmp_path):
    import json

    from own_names_bench.run import run

    out = tmp_path / "r"
    out.mkdir()
    (out / "run.json").write_text(json.dumps({"system": "other", "dataset_fingerprint": "x"}))
    with pytest.raises(SystemExit):
        run(bench, _Fake(), out, chapters=False, limit=1, only="", hourly_usd=None)
    out2 = tmp_path / "r2"
    run(bench, _Fake("a"), out2, chapters=False, limit=0, only="clip/none-such", hourly_usd=None)  # writes run.json, no passes
    with pytest.raises(SystemExit):
        run(bench, _Fake("b"), out2, chapters=False, limit=0, only="clip/none-such", hourly_usd=None)


def test_incomplete_run_is_flagged(bench):
    from own_names_bench.passes import all_passes
    from own_names_bench.report import completeness

    ps = all_passes(bench, ("none",), True)
    rows = {p.id: {"list_sha": p.list_sha, "text": ""} for p in ps[:-1]}
    c = completeness(bench, {"system": "qwen", "variants": ["none"]}, rows, {})
    assert not c["complete"] and c["missing"] == 1


def test_suite_insertions_tell_names_of_the_recording_from_others_and_skip_non_names(bench):
    """In a calls stretch, a name taught in this call counts as an insertion but not as one from another
    recording (the reference may have missed it being said); a name taught in another call counts as both;
    an ordinary word the name finder listed (`not_names`) counts as neither, and is never a scored mention."""
    from own_names_bench.score import score

    calls = bench.suites["calls"]
    texts = _reference_texts(bench)
    skip = set(calls.m["not_names"])
    assert skip and not any(mn["entry"] in skip for mn in score(bench, texts)["suites"]["calls"]["mentions"])
    nf = next(x for x in calls.m["name_free"] if skip & set(calls.lists[f"own:{calls.clips[x['clip']]['book']}"]["entries"]))
    clip = calls.clips[nf["clip"]]
    book = clip["book"]
    entries = calls.lists[f"own:{book}"]["entries"]
    own = next(e for e in entries if calls.entries[e]["book"] == book and e not in skip)
    other = next(e for e in entries if calls.entries[e]["book"] != book and e not in skip)
    pid = f"suite/calls/clip/{nf['clip']}/own"
    for written, inserted, foreign in ((calls.entries[own]["written"], True, False), (calls.entries[other]["written"], True, True)):
        texts[pid] = clip["reference"] + " " + written
        row = next(r for r in score(bench, texts)["suites"]["calls"]["name_free"] if r["clip"] == nf["clip"])
        assert (row["own_inserted"], row["own_inserted_foreign"]) == (inserted, foreign), written
    junk = next(e for e in entries if e in skip)
    texts[pid] = clip["reference"] + " " + calls.entries[junk]["written"]
    row = next(r for r in score(bench, texts)["suites"]["calls"]["name_free"] if r["clip"] == nf["clip"])
    assert not row["own_inserted"] and not row["own_inserted_foreign"]


def test_a_run_without_chapters_is_complete_without_them(bench):
    from own_names_bench.passes import all_passes
    from own_names_bench.report import completeness

    ps = all_passes(bench, ("none",), False)
    rows = {p.id: {"list_sha": p.list_sha, "text": ""} for p in ps}
    assert not completeness(bench, {"system": "qwen", "variants": ["none"]}, rows, {})["complete"]
    c = completeness(bench, {"system": "qwen", "variants": ["none"], "chapters": False}, rows, {})
    assert c["complete"] and c["expected"] == len(ps)


def test_a_stale_run_is_listed_but_left_out_of_the_tables():
    from own_names_bench.report import render

    comp = {"variants": ["none"], "chapters": True, "expected": 1, "completed": 1, "failed": 0, "stale": 0, "missing": 0, "complete": True}
    meta = {"system": "qwen", "stale": "code not recorded", "config": {}, "machine": {}, "commands": [{"argv": "", "started": ""}]}
    md = render({"old": {"meta": meta, "summary": {}, "items": {}, "completeness": comp}}, None)
    assert "stale: left out of every table below** (code not recorded)" in md
    assert "| old | n/a" not in md and "- **old**" not in md
