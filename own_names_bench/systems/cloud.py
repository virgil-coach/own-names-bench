"""Hosted recognizers. Keys come from the environment only (ELEVENLABS_API_KEY, DEEPGRAM_API_KEY);
they are never logged or written. Only the benchmark's public-domain audio is sent."""

import os
import time
from pathlib import Path

import requests

from .base import Fit, Output, System, unique

PRICES_CHECKED = "2026-10-13"


class ServiceError(RuntimeError):
    pass


def _post(url: str, retries: int = 5, **kw) -> requests.Response:
    """Retries only transport errors, 429 and 5xx; a 4xx answer is returned to the caller."""
    for attempt in range(retries):
        try:
            r = requests.post(url, **kw)
        except requests.RequestException as e:
            if attempt == retries - 1:
                raise ServiceError(f"{type(e).__name__}") from e
            time.sleep(2 * (attempt + 1))
            continue
        if r.status_code == 429 or r.status_code >= 500:
            if attempt == retries - 1:
                raise ServiceError(f"HTTP {r.status_code}: {r.text[:200]}")
            time.sleep(3 * (attempt + 1))
            continue
        return r
    raise ServiceError("unreachable")


class ElevenLabs(System):
    """ElevenLabs Scribe v2 (batch), names as `keyterms`.

    Documented limits (api-reference/speech-to-text/convert, checked 2026-10-13): at most 1,000
    keyterms, each under 50 characters and at most 5 words, none of < > { } [ ] \\. More than 100
    keyterms bills at least 20 seconds per request. Keyterms add 20% ($0.05/h) to the price."""

    name = "elevenlabs"
    kind = "cloud"
    workers = 4
    MODEL = "scribe_v2"
    MAX_TERMS = 1000
    BAD = set("<>{}[]\\")

    def config(self) -> dict:
        return {"service": "ElevenLabs Speech to Text", "endpoint": "https://api.elevenlabs.io/v1/speech-to-text",
                "model_id": self.MODEL, "language_code": "en", "tag_audio_events": False, "temperature": 0.0, "seed": 0,
                "list_feature": "keyterms", "limits": "<=1000 terms, each <50 chars and <=5 words, no <>{}[]\\",
                "fit": "drop terms that break a per-term rule, then keep the first 1000 (most frequent in the book first)"}

    def price(self) -> dict:
        return {"usd_per_audio_hour": 0.22, "usd_per_audio_hour_with_list": 0.27, "min_billable_s_over_100_terms": 20,
                "checked": PRICES_CHECKED, "source": "https://elevenlabs.io/pricing/api"}

    def start(self) -> None:
        if not os.environ.get("ELEVENLABS_API_KEY"):
            raise SystemExit("ELEVENLABS_API_KEY is not set (run under `op run --env-file`)")

    def fit(self, names: list[str]) -> Fit:
        ok, dropped = [], []
        for n in unique(names):
            if len(n) >= 50 or len(n.split()) > 5 or self.BAD & set(n):
                dropped.append(n)
            else:
                ok.append(n)
        return Fit(ok[: self.MAX_TERMS], f"{min(len(ok), self.MAX_TERMS)} of {len(unique(names))} names", dropped + ok[self.MAX_TERMS :])

    def transcribe(self, audio: Path, names: list[str], entries: list[dict]) -> Output:
        data = [("model_id", self.MODEL), ("language_code", "en"), ("tag_audio_events", "false"),
                ("temperature", "0"), ("seed", "0")] + [("keyterms", n) for n in names]
        r = _post("https://api.elevenlabs.io/v1/speech-to-text", headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
                  data=data, files={"file": (audio.name, audio.read_bytes(), "audio/flac")}, timeout=900)
        if r.status_code >= 400:
            raise ServiceError(f"HTTP {r.status_code}: {r.text[:300]}")
        j = r.json()
        return Output(j.get("text") or "", extra={"language_code": j.get("language_code")})


class Deepgram(System):
    """Deepgram Nova-3 (pre-recorded), names as repeated `keyterm` parameters.

    Documented limit (docs/keyterm, checked 2026-10-13): 500 tokens of keyterms per request, by
    Deepgram's own tokenizer, which is not published. The list is fitted by asking: when the
    service refuses the full list, the longest prefix it accepts is found by binary search on
    half a second of silence, and recorded with the pass. Keyterms add $0.0013/min."""

    name = "deepgram"
    kind = "cloud"
    variants = ("none", "own")  # 500 keyterm tokens cannot hold the 902-name all-books list
    workers = 4
    MODEL = "nova-3"

    def __init__(self) -> None:
        import io

        import numpy as np
        import soundfile as sf

        self.accepted: dict[tuple[str, ...], int] = {}
        self.by_head: dict[str, int] = {}
        buf = io.BytesIO()
        sf.write(buf, np.zeros(8000, dtype=np.int16), 16000, format="FLAC")
        self.silence = buf.getvalue()

    def config(self) -> dict:
        return {"service": "Deepgram pre-recorded", "endpoint": "https://api.deepgram.com/v1/listen", "model": self.MODEL,
                "language": "en", "smart_format": True, "list_feature": "keyterm",
                "limits": "500 keyterm tokens per request (Deepgram's tokenizer, unpublished)",
                "fit": "the longest prefix of the list (most frequent first) the service accepts, found by binary search with half a second of silence (refused requests are not billed)"}

    def price(self) -> dict:
        return {"usd_per_audio_hour": 0.0043 * 60, "usd_per_audio_hour_with_list": (0.0043 + 0.0013) * 60,
                "checked": PRICES_CHECKED, "source": "https://deepgram.com/pricing"}

    def start(self) -> None:
        if not os.environ.get("DEEPGRAM_API_KEY"):
            raise SystemExit("DEEPGRAM_API_KEY is not set (run under `op run --env-file`)")

    def _call(self, audio: bytes, names: list[str]) -> requests.Response:
        params = [("model", self.MODEL), ("language", "en"), ("smart_format", "true")] + [("keyterm", n) for n in names]
        return _post("https://api.deepgram.com/v1/listen", params=params, data=audio, timeout=900,
                     headers={"Authorization": f"Token {os.environ['DEEPGRAM_API_KEY']}", "Content-Type": "audio/flac"})

    def _accepts(self, names: list[str]) -> bool:
        """Does the service take this keyterm list? Asked with half a second of silence."""
        r = self._call(self.silence, names)
        if r.status_code < 400:
            return True
        if r.status_code == 400 and "keyterm" in r.text.lower():
            return False
        raise ServiceError(f"HTTP {r.status_code}: {r.text[:300]}")

    def _longest(self, names: list[str]) -> int:
        """The longest prefix the service accepts (the full list was refused): binary search,
        starting next to what this book's other lists were accepted at."""
        key = tuple(names)
        if key in self.accepted:
            return self.accepted[key]
        guess = self.by_head.get(names[0])
        lo, hi = 0, len(names) - 1  # lo is accepted (empty list), len(names) was refused
        if guess is not None and guess < len(names):
            if self._accepts(names[:guess]):
                lo = guess
                hi = min(hi, guess + 1) if not self._accepts(names[: guess + 1]) else hi
                if hi == guess + 1 and hi <= len(names) - 1 and self._accepts(names[:hi]):
                    lo = hi
            else:
                hi = guess - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self._accepts(names[:mid]):
                lo = mid
            else:
                hi = mid - 1
        self.accepted[key] = lo
        self.by_head[names[0]] = lo
        return lo

    def transcribe(self, audio: Path, names: list[str], entries: list[dict]) -> Output:
        body = audio.read_bytes()
        n = self.accepted.get(tuple(names), len(names))
        t0 = time.perf_counter()
        r = self._call(body, names[:n])
        if r.status_code == 400 and "keyterm" in r.text.lower() and n > 0:
            n = self._longest(names)
            t0 = time.perf_counter()
            r = self._call(body, names[:n])
        took = time.perf_counter() - t0
        if r.status_code >= 400:
            raise ServiceError(f"HTTP {r.status_code}: {r.text[:300]}")
        alt = r.json()["results"]["channels"][0]["alternatives"][0]
        how = f"service accepted {n} of {len(names)} names (longest accepted prefix)" if n < len(names) else f"{n} of {n} names"
        return Output(alt.get("transcript") or "", sent=names[:n], how=how, latency_s=took,
                      extra={"model_info": r.json().get("metadata", {}).get("model_info")})
