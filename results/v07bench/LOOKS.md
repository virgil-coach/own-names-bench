# Looks at the v1.2.0 audiobook suite (results/v07bench/PROTOCOL.md)

Every scoring of a system on the own-names-bench v1.2.0 audiobook clips under the 2026-10-17 protocol is a row here.
These numbers are a selection target, not an unbiased held-out estimate. Aggregates only: false insertions = name-free
items with a listed name inserted (of 408), names right (of 1,107 mentions), untaught overwritten (of 1,107), ordinary-word
error; 95% intervals clustered by book.

## Before the protocol (reference rows, reused, not re-run)

| System | Adapter SHA-256 | Date | False insertions | Names right | Untaught overwritten | Word error |
| --- | --- | --- | --- | --- | --- | --- |
| ElevenLabs Scribe v2 (keyterms) | n/a | published v1.2.0 run | 0.2 [0.0, 0.7] (1/408) | 92.2 [87.6, 97.2] | 3.3 [1.1, 5.8] | 1.7 [1.4, 1.9] |
| v0.3.0 + fixes (ours-fixed) | v0.3.0 hub adapter | results/diag | 4.4 [0.7, 10.5] (18/408) | 96.4 [94.7, 98.4] | 6.8 [2.4, 10.7] | 2.7 [2.4, 3.1] |
| v6j finalist + guard + re-read | f4f39c56f8d3535bb25e01e215f4431591e480688ee293fe96522fb41415706d | 2026-10-16 (v0.6 final) | 3.4 [0.5, 8.6] (14/408) | 94.9 [92.7, 97.2] | 4.7 [1.5, 7.6] | 2.7 [2.3, 3.1] |

## Under the protocol

| # | System | Adapter SHA-256 | Date | False insertions | Names right | Untaught overwritten | Word error |
| --- | --- | --- | --- | --- | --- | --- | --- |
