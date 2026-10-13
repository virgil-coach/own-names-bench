from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Fit:
    sent: list[str]
    how: str = ""
    dropped: list[str] = field(default_factory=list)


@dataclass
class Output:
    text: str
    sent: list[str] | None = None      # when the system had to shrink the list on the service's say-so
    how: str = ""
    extra: dict = field(default_factory=dict)
    latency_s: float | None = None     # the request that produced the text, when list fitting took extra calls


def unique(names: list[str]) -> list[str]:
    """Spellings in order, each once (two books may share a name)."""
    seen: set[str] = set()
    out = []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


class System:
    name: str = ""
    variants: tuple[str, ...] = ("none", "own", "all")   # which clip list variants it can take
    workers: int = 1                                      # passes in flight at once
    kind: str = "local"                                   # "local" or "cloud"

    def config(self) -> dict:
        """Everything that fixes what this system does: model ids, revisions, parameters, limits."""
        raise NotImplementedError

    def price(self) -> dict:
        return {}

    def start(self) -> None:
        """Load models / check keys. Called once before the first pass."""

    def fit(self, names: list[str]) -> Fit:
        return Fit(unique(names), "all names")

    def transcribe(self, audio: Path, names: list[str], entries: list[dict]) -> Output:
        raise NotImplementedError

    def stop(self) -> None:
        pass
