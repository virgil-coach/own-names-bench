#!/bin/bash
BK=/gpu-cli-workspaces/jameslal/lore-books; SP=/gpu-cli-workspaces/jameslal/lore-spot
nvidia-smi --query-gpu=name --format=csv,noheader; df -h /gpu-cli-workspaces | tail -1
ls $BK | head; ls $BK/splits; wc -l $BK/splits/dev.jsonl; head -c 1500 $BK/splits/dev.jsonl; echo
ls $SP | head -20; ls $SP/pools; head -c 1200 $SP/books_dev.jsonl; echo
python3 -c "
import json
p=json.load(open('$SP/pools/dev.json'))
print(list(p)); g=list(p['pools'])[:8]; print(g)
for k in g[:3]: print(k, {a:len(b) for a,b in p['pools'][k].items()})
print(p['entries'][0]); print(len(p['entries']))
"
ls /gpu-cli-workspaces/jameslal/ | head -40
