"""Text normalization. Two tokenizations, both fixed by this file and the vendored Whisper normalizer.

name tokens       used to find names. NFC, curly apostrophes made straight, lower case, split on
                  anything that is not a letter, digit or word-internal apostrophe (so hyphens and
                  spaces are the same), a trailing possessive 's dropped. Letters, including
                  diacritics, must match exactly: "Carce" is not "Carcë".
ordinary tokens   used for word error outside names: OpenAI Whisper's EnglishTextNormalizer
                  (vendored at commit 86098128, MIT), the normalizer of the Open ASR Leaderboard.
                  It lower-cases, drops punctuation and diacritics, writes numbers as digits and
                  standardizes British spellings.
"""

import re
import unicodedata
from functools import lru_cache

from .whisper_normalizer import EnglishTextNormalizer

NORMALIZATION_VERSION = "1"
_APOS = str.maketrans({"’": "'", "‘": "'", "ʼ": "'", "`": "'", "´": "'"})
_TOKEN = re.compile(r"[^\W_]+(?:'[^\W_]+)*")
_EN = EnglishTextNormalizer()


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text).translate(_APOS)


def _clean_token(tok: str) -> str:
    tok = tok.lower()
    if tok.endswith("'s") and len(tok) > 2:
        tok = tok[:-2]
    return tok


def name_tokens_spans(text: str) -> list[tuple[str, int, int]]:
    """Name tokens of `text` with their character spans in nfc(text)."""
    t = nfc(text)
    return [(_clean_token(m.group(0)), m.start(), m.end()) for m in _TOKEN.finditer(t)]


def name_tokens(text: str) -> list[str]:
    return [t for t, _, _ in name_tokens_spans(text)]


@lru_cache(maxsize=65536)
def name_key(spelling: str) -> tuple[str, ...]:
    return tuple(name_tokens(spelling))


def ordinary_tokens(text: str) -> list[str]:
    return _EN(nfc(text)).split()


@lru_cache(maxsize=65536)
def ordinary_key(word: str) -> tuple[str, ...]:
    return tuple(ordinary_tokens(word))


def find_all(tokens: list[str], key: tuple[str, ...]) -> list[int]:
    """Start indices where the token sequence `key` occurs in `tokens`."""
    n = len(key)
    if n == 0:
        return []
    first = key[0]
    return [i for i in range(len(tokens) - n + 1) if tokens[i] == first and tuple(tokens[i : i + n]) == key]
