"""The passes: one recording sent to a system once, with one name list.

Clip passes (variant is the name list used):
  clip/<clip>/none                  no list
  clip/<clip>/own                   the book's own list (every name of the book)
  clip/<clip>/own-minus/<entry>     that list without the name said in the clip ("untaught")
  clip/<clip>/all                   all-books list: the book's names first, then every other book's
  clip/<clip>/all-minus/<entry>
  clip/<clip>/own-xr/<entry>        (systems taught by recording) the own list, with the spoken
                                    name taught by another reader's recording of it
Chapter passes:
  chapter/<id>/none, chapter/<id>/taught (the book's list), chapter/<id>/untaught (that list
  without every other name, the chapter's `untaught` entries)

"Without the name" removes every entry spelled the same way (normalized, text.name_key): two
books may both list "Cythera", and the untaught pass must not leave either. `minus` asserts it.

Every system gets the same entries in the same order (most frequent in the book first). How a
system fits them to its own limits is the system's `fit`, recorded with every pass, and each
pass carries a fingerprint of its list so a changed list is never answered from an old run.
"""

import hashlib
from dataclasses import dataclass, field

from .data import Bench
from .text import name_key

VARIANTS = ("none", "own", "all", "xr")


@dataclass(frozen=True)
class Pass:
    id: str
    task: str            # "clip" | "chapter"
    audio: str           # path relative to the dataset root
    seconds: float
    variant: str         # "none" | "own" | "all" | "xr" | "chapter"
    entries: tuple[str, ...]
    # entry -> entry whose taught recording stands in for it (cross-reader passes)
    samples: tuple[tuple[str, str], ...] = field(default=())
    suite: str = ""      # "" for the audiobooks, else the suite the clip belongs to

    @property
    def list_sha(self) -> str:
        h = hashlib.sha256("\n".join(self.entries).encode())
        for a, s in self.samples:
            h.update(f"\n{a}<-{s}".encode())
        return h.hexdigest()[:16]


def minus(b: Bench, entries: list[str], target: str) -> list[str]:
    """The list without the target name: every entry spelled like it is removed."""
    key = name_key(b.entries[target]["written"])
    out = [e for e in entries if name_key(b.entries[e]["written"]) != key]
    assert all(name_key(b.entries[e]["written"]) != key for e in out)
    return out


def cross_reader(b: Bench) -> dict[str, str]:
    """mention id -> an entry of the same spelling taught by a different reader (first in entry order)."""
    by_key: dict[tuple[str, ...], list[str]] = {}
    for e in sorted(b.entries):
        by_key.setdefault(name_key(b.entries[e]["written"]), []).append(e)
    out = {}
    for mn in b.m["mentions"]:
        me = b.entries[mn["entry"]]
        alt = [e for e in by_key[name_key(me["written"])] if e != mn["entry"] and b.entries[e]["reader"] != me["reader"]]
        if alt:
            out[mn["id"]] = alt[0]
    return out


def clip_passes(b: Bench, variants: tuple[str, ...]) -> list[Pass]:
    out: dict[str, Pass] = {}

    def add(clip: str, key: str, variant: str, entries: list[str], samples: tuple = ()) -> None:
        pid = f"{b.prefix}clip/{clip}/{key}"
        if pid not in out:
            c = b.clips[clip]
            out[pid] = Pass(pid, "clip", c["audio"], c["seconds"], variant, tuple(entries), samples, b.name)

    used = [mn["clip"] for mn in b.m["mentions"]] + [nf["clip"] for nf in b.m["name_free"]]
    for clip in used:
        book = b.clips[clip]["book"]
        if "none" in variants:
            add(clip, "none", "none", [])
        for v in ("own", "all"):
            if v in variants and f"{v}:{book}" in b.lists:
                add(clip, v, v, b.lists[f"{v}:{book}"]["entries"])
    xr = cross_reader(b) if "xr" in variants and not b.name else {}
    for mn in b.m["mentions"]:
        book = b.clips[mn["clip"]]["book"]
        for v in ("own", "all"):
            if v in variants and f"{v}:{book}" in b.lists:
                add(mn["clip"], f"{v}-minus/{mn['entry']}", v, minus(b, b.lists[f"{v}:{book}"]["entries"], mn["entry"]))
        if mn["id"] in xr:
            add(mn["clip"], f"own-xr/{mn['entry']}", "xr", b.lists[f"own:{book}"]["entries"], ((mn["entry"], xr[mn["id"]]),))
    return sorted(out.values(), key=lambda p: p.id)


def chapter_passes(b: Bench) -> list[Pass]:
    out = []
    for ch in b.m["chapters"]:
        full = b.lists[ch["list"]]["entries"]
        untaught = list(ch["untaught"])
        rest = full
        for e in untaught:
            rest = minus(b, rest, e)
        for key, entries in (("none", []), ("taught", full), ("untaught", rest)):
            out.append(Pass(f"chapter/{ch['id']}/{key}", "chapter", ch["audio"], ch["seconds"], "chapter", tuple(entries)))
    return out


def all_passes(b: Bench, variants: tuple[str, ...], chapters: bool = True, suites: bool = True) -> list[Pass]:
    out = clip_passes(b, variants) + (chapter_passes(b) if chapters else [])
    if suites:
        for s in (b.suites or {}).values():
            out += clip_passes(s, tuple(v for v in variants if v in ("none", "own")))
    return out


def view(b: Bench, p: Pass) -> Bench:
    """The data a pass belongs to: the audiobooks or one suite."""
    return b.suites[p.suite] if p.suite else b
