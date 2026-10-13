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


@pytest.fixture(scope="module")
def bench():
    root = default_dir()
    if not (root / "manifest.json").exists():
        pytest.skip("dataset not present")
    return load(root, verify=False)


def _reference_texts(b):
    texts = {}
    for p in all_passes(b, ("none", "own", "all"), True):
        if p.task == "clip":
            clip = p.id.split("/")[1]
            texts[p.id] = b.clips[clip]["reference"]
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
