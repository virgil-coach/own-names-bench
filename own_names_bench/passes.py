"""The passes: one recording sent to a system once, with one name list.

Clip passes (variant is the name list used):
  clip/<clip>/none                  no list
  clip/<clip>/own                   the book's own list (every name of the book)
  clip/<clip>/own-minus/<entry>     the same list without the name said in the clip ("untaught")
  clip/<clip>/all                   all-books list: the book's names first, then every other book's
  clip/<clip>/all-minus/<entry>
Chapter passes:
  chapter/<id>/none, chapter/<id>/taught (the book's list), chapter/<id>/untaught (that list
  without every other name, the chapter's `untaught` entries)

Every system gets the same entries in the same order (most frequent in the book first). How a
system fits them to its own limits is the system's `fit`, recorded with every pass.
"""

from dataclasses import dataclass

from .data import Bench

VARIANTS = ("none", "own", "all")


@dataclass(frozen=True)
class Pass:
    id: str
    task: str            # "clip" | "chapter"
    audio: str           # path relative to the dataset root
    seconds: float
    variant: str         # "none" | "own" | "all" | "chapter"
    entries: tuple[str, ...]


def clip_passes(b: Bench, variants: tuple[str, ...]) -> list[Pass]:
    out: dict[str, Pass] = {}

    def add(clip: str, key: str, variant: str, entries: list[str]) -> None:
        pid = f"clip/{clip}/{key}"
        if pid not in out:
            c = b.clips[clip]
            out[pid] = Pass(pid, "clip", c["audio"], c["seconds"], variant, tuple(entries))

    used = [mn["clip"] for mn in b.m["mentions"]] + [nf["clip"] for nf in b.m["name_free"]]
    for clip in used:
        book = b.clips[clip]["book"]
        if "none" in variants:
            add(clip, "none", "none", [])
        for v in ("own", "all"):
            if v in variants:
                add(clip, v, v, b.lists[f"{v}:{book}"]["entries"])
    for mn in b.m["mentions"]:
        book = b.clips[mn["clip"]]["book"]
        for v in ("own", "all"):
            if v in variants:
                full = b.lists[f"{v}:{book}"]["entries"]
                add(mn["clip"], f"{v}-minus/{mn['entry']}", v, [e for e in full if e != mn["entry"]])
    return sorted(out.values(), key=lambda p: p.id)


def chapter_passes(b: Bench) -> list[Pass]:
    out = []
    for ch in b.m["chapters"]:
        full = b.lists[ch["list"]]["entries"]
        untaught = set(ch["untaught"])
        for key, entries in (("none", []), ("taught", full), ("untaught", [e for e in full if e not in untaught])):
            out.append(Pass(f"chapter/{ch['id']}/{key}", "chapter", ch["audio"], ch["seconds"], "chapter", tuple(entries)))
    return out


def all_passes(b: Bench, variants: tuple[str, ...], chapters: bool = True) -> list[Pass]:
    return clip_passes(b, variants) + (chapter_passes(b) if chapters else [])
