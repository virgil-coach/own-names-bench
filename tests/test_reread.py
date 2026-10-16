"""The re-read's plumbing with a stub writer (no models): which windows are re-read, with what span and list, and
what is kept. The rule is the engine's (detailkeeper main ffc673a, detailkeeper-bench)."""

from dataclasses import dataclass

import numpy as np
import pytest

pytest.importorskip("torch")

from own_names_bench.ours_ref.reread import extract  # noqa: E402
from own_names_bench.ours_ref.spotter import Hit, Term  # noqa: E402
from own_names_bench.systems.ours_fixed import OursFixed  # noqa: E402


@dataclass
class W:
    audio_from_s: float
    end_s: float
    audio: np.ndarray


def said(seconds: float) -> np.ndarray:
    return (0.3 * np.sin(np.arange(int(seconds * 16000)) * 0.2)).astype(np.float32)


class StubWriter:
    def __init__(self, answer: str) -> None:
        self.answer, self.calls = answer, []

    def write(self, audio, entries):
        self.calls.append((len(audio) / 16000, [e[0] for e in entries]))
        return self.answer


def system(answer: str) -> OursFixed:
    s = OursFixed.__new__(OursFixed)
    s.level, s.writer = False, StubWriter(answer)
    s.clips = {"eu": np.zeros(160, np.float32), "ann": np.zeros(160, np.float32)}
    return s


def hit(key: str, written: str, score: float) -> Hit:
    return Hit(Term(key, written, written), score, -0.7)


def test_extract_matches_the_engine_tests():
    assert extract("and so we went home. Sure. Then the minister said", "we went home.", "Turkey.", "Then the minister said that") == "Sure."
    assert extract("we went home. Sure, Erdogan said. Then", "and so we went home.", "Sure.", "Then the") == "Sure, Erdogan said."
    assert extract("home sure", "home", "", "next") == "sure"
    assert extract("totally different words", "a b", "c", "d") is None
    assert extract("", "a", "b", "c") is None


def test_a_lone_window_keeps_its_first_pass():
    s = system("Under the EU.")
    x = said(0.8)
    wins = [{}]
    out = s._reread(x, [W(0.0, 0.8, x)], [[hit("eu", "EU", 3.0)]], ["Under the."], wins)
    assert out == ["Under the."] and s.writer.calls == []
    assert wins[0]["reread"]["before_in"] is False and wins[0]["reread"]["after_in"] is False


def test_a_short_window_is_reread_with_its_neighbours_and_the_merged_list():
    s = system("we went home. Sure. Then the minister")
    x = said(12.0)
    windows = [W(0.0, 5.0, x[:80000]), W(5.0, 6.0, x[80000:96000]), W(6.0, 12.0, x[96000:])]
    hits = [[hit("ann", "Ann", 1.0)], [hit("eu", "EU", 2.0)], [hit("ann", "Ann", 4.0)]]
    wins = [{}, {}, {}]
    out = s._reread(x, windows, hits, ["we went home.", "Turkey.", "Then the minister said"], wins)
    # the long windows are not re-read (6 s and 5 s of speech); the short one is, 1 s + 4 s either side
    assert [len(c) for c in [s.writer.calls]] == [1]
    seconds, names = s.writer.calls[0]
    assert seconds == pytest.approx(9.0)
    assert names == ["Ann", "EU"]  # best score first, each entry once
    assert out == ["we went home.", "Sure.", "Then the minister said"]
    assert wins[1]["reread"]["used"] is True


def test_a_reread_that_recites_or_is_empty_is_not_used():
    for answer in ("", "Ann, EU, Ann, EU, Ann"):
        s = system(answer)
        x = said(8.0)
        windows = [W(0.0, 4.0, x[:64000]), W(4.0, 5.0, x[64000:80000]), W(5.0, 8.0, x[80000:])]
        hits = [[], [hit("eu", "EU", 2.0)], []]
        out = s._reread(x, windows, hits, ["a b c", "Yes.", "d e"], [{}, {}, {}])
        assert out[1] == "Yes."
