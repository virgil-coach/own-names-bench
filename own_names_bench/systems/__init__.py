"""The systems under test. Each gets the same ordered name list for a pass and passes it on through
its own documented custom-vocabulary feature, fitted to that feature's documented limits."""

from collections.abc import Callable

from .base import System


def _elevenlabs() -> System:
    from .cloud import ElevenLabs

    return ElevenLabs()


def _deepgram() -> System:
    from .cloud import Deepgram

    return Deepgram()


def _whisper() -> System:
    from .whisper import Whisper

    return Whisper()


def _parakeet() -> System:
    from .parakeet import Parakeet

    return Parakeet()


def _qwen() -> System:
    from .qwen import PlainQwen

    return PlainQwen(context=False)


def _qwen_context() -> System:
    from .qwen import PlainQwen

    return PlainQwen(context=True)


def _ours_torch() -> System:
    from .ours_torch import OursTorch

    return OursTorch()


def _ours_mlx() -> System:
    from .ours_mlx import OursMlx

    return OursMlx()


def _ablate(name: str, **kw) -> Callable[[], System]:
    def make() -> System:
        from .ours_ablate import OursAblate

        return OursAblate(name, **kw)

    return make


# diagnosis only (branch diag/v12-conversation): see systems/ours_ablate.py
ABLATIONS: dict[str, Callable[[], System]] = {
    "ours-trace": _ablate("ours-trace"),
    "ours-top40": _ablate("ours-top40", top=40, variants=("own",)),
    "ours-wholeclip": _ablate("ours-wholeclip", cutter="qwen"),
    "ours-adapter-context": _ablate("ours-adapter-context", cutter="qwen", prompt="context", variants=("own",)),
    "ours-level": _ablate("ours-level", level=True, variants=("own",)),
}


def _fixed() -> System:
    from .ours_fixed import OursFixed

    return OursFixed()


def _guarded() -> System:
    from .ours_fixed import OursFixed

    return OursFixed(name="ours-guard", name_guard=True)

def _reread() -> System:
    from .ours_fixed import OursFixed

    return OursFixed(name="ours-reread", name_guard=True, reread=True)

SYSTEMS: dict[str, Callable[[], System]] = {
    **ABLATIONS,
    "ours-fixed": _fixed,         # ours + empty-answer guard, level-match, short windows (branch fix/v12-pipeline)
    "ours-guard": _guarded,       # ours-fixed + the name guard (branch fix/name-guard; detailkeeper engine/name-guard)
    "ours-reread": _reread,       # ours-guard + re-read of short windows (branch v06/final; detailkeeper main ffc673a)
    "ours": _ours_torch,          # the reference runner (PyTorch; CUDA, CPU or MPS)
    "ours-mlx": _ours_mlx,        # the Detail Keeper engine itself (Rust, MLX, Apple silicon)
    "elevenlabs": _elevenlabs,
    "deepgram": _deepgram,
    "whisper": _whisper,
    "parakeet": _parakeet,
    "qwen": _qwen,
    "qwen-context": _qwen_context,
}
