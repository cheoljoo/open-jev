# openjev vs laya

| | openjev | laya |
|---|---|---|
| Author | AlexWortega | NandhaKishorM / Convai Innovations |
| Base | Qwen3.5 4B/2B/0.8B, NLI cross-encoder | own encoders (~0.3-0.4B), optional vega reader |
| Created | 2026-09-16 | 2026-09-18 |
| Last update (as checked 2026-11-15) | 2026-10-01 | 2026-11-14 (PyPI 0.4.32) |
| Distribution | Hugging Face weights | `pip install laya`, Hub checkpoints |
| Approach | one forward pass per option (entailment) | one forward pass for all options |

## Caveats

- openjev's model card reports JevBench public 0.814 for 4B v5 (Jev 1.13: 0.866). It states the model is **not hardened against prompt injection**
  (one adversarial line drops accuracy on 150 items from 0.833 to 0.467) and was trained on test splits of several public benchmarks, so those scores are not meaningful.
  Do not use it as a standalone safety guard.
- laya reports its own benchmark numbers; no independent comparison on the same benchmark was run here.
- A single request on the sample billing text: openjev ~0.07 s, laya ~0.27 s (n=1, not a benchmark).

## Sources

- https://huggingface.co/AlexWortega/openjev
- https://github.com/NandhaKishorM/laya , https://pypi.org/project/laya/
