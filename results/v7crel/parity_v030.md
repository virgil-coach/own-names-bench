# Writer parity, v0.3.0 (harness check): MLX affine 8-bit (writer_replay, engine af939d6, Mac mini) vs torch float32 + peft (ours_ref.Writer, MPS, Mac Studio)

lore-poc bigspot pool/test sub200 export, 400 stratified calls (diag/writer_parity.py prep --n 400, seed 17). Adapter 67dbabef…7f55.

same text (normalized): 376/400 = 94.0%
| group | calls | names right MLX 8-bit | names right torch | right on one side only (MLX / torch) | a listed name not in the reference written (MLX / torch) |
| --- | --- | --- | --- | --- | --- |
| audiobooks, invented names, known | 42 | 41 | 41 | 0 / 0 | 1 / 0 |
| audiobooks, invented names, unknown | 46 | 0 | 0 | 0 / 0 | 0 / 0 |
| audiobooks, name-free, name-free | 44 | 0 | 0 | 0 / 0 | 2 / 1 |
| audiobooks, traditional names, known | 47 | 46 | 45 | 1 / 0 | 4 / 4 |
| audiobooks, traditional names, unknown | 41 | 0 | 0 | 0 / 0 | 6 / 6 |
| public video, easy names, known | 48 | 48 | 48 | 0 / 0 | 0 / 0 |
| public video, easy names, unknown | 43 | 0 | 0 | 0 / 0 | 1 / 1 |
| public video, hard names, known | 54 | 47 | 47 | 0 / 0 | 1 / 1 |
| public video, hard names, unknown | 35 | 0 | 0 | 0 / 0 | 2 / 2 |
