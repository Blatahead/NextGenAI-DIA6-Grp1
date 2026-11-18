# TD 2 — Step 3: the routing rule (Pair C: Emma, Bart)

Report: [`reports/td2.md`, section 3](../../reports/td2.md#3-step-3--the-routing-rule-pair-c).

| File | Content |
|---|---|
| `routing-rule-td2.md` | The one-page routing rule: TD 1 rates per question family, the rule, the simulator scenarios, limits |
| `routage-td2-before.jsonl` | Simulator output with the kit's rule (7 scenarios) |
| `routage-td2-after.jsonl` | Simulator output with our rule (the same 7 scenarios plus 5 added) |

The simulator itself, with our `RESOURCES` and `choose`, is the kit file [`kit/atelier-routage.py`](../../kit/atelier-routage.py) (completed in place).

Replay from the repository root (no call, no key):

```bash
python kit/atelier-routage.py                         # reproduces routage-td2-after.jsonl
python kit/atelier-routage.py --scenario deferrable   # one scenario
```
