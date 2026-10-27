"""own-names-bench: spelling taught names in speech, scored the same way for every recognizer."""

BENCH_NAME = "own-names-bench"
BENCH_VERSION = "1.3.0"
# the layout of a dataset folder (manifest.json, suites/<name>/suite.json); a manifest's `version` is this.
# v1.3.0 keeps the v1.2.0 layout, so the v1.2.0 data and the sealed v1.3 suites are published byte for byte as scored
DATA_FORMAT = "1.2.0"
