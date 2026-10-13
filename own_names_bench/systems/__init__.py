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


SYSTEMS: dict[str, Callable[[], System]] = {
    "ours": _ours_torch,          # the reference runner (PyTorch; CUDA, CPU or MPS)
    "ours-mlx": _ours_mlx,        # the Detail Keeper engine itself (Rust, MLX, Apple silicon)
    "elevenlabs": _elevenlabs,
    "deepgram": _deepgram,
    "whisper": _whisper,
    "parakeet": _parakeet,
    "qwen": _qwen,
    "qwen-context": _qwen_context,
}
