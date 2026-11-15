# API

Base URLs: `http://<HOST>:8100` (openjev) and `http://<HOST>:8200` (laya). Interactive Swagger UI: `/docs` on each.

## Question types

| type | `criteria` | answer |
|---|---|---|
| `choice` | `{"label": "rubric", ...}` (2+ options) | `choice`, `probabilities` |
| `score` | `["low", "mid", "high"]` (2+ labels, low to high) | `probabilities`; openjev adds `score` (index), laya a continuous `score` |
| `noul` | none (yes/no) | `noul` = P(yes) (openjev also `answer`) |

Sending `"criteria": "string"` (the placeholder Swagger used to show) returns `422 choice needs criteria: {label: rubric} with >=2 options`.

## openjev (:8100)

| Endpoint | Purpose |
|---|---|
| `GET /health` | status |
| `POST /v1/systemone` (alias `/predict`) | typed decisions |
| `POST /v1/entail` | `P(entailment)` of each hypothesis given a premise (rerank, grade, guard) |

```bash
curl -X POST http://<HOST>:8100/v1/systemone -H 'Content-Type: application/json' -d '{
  "state": "We were billed twice for March. Please refund it today.",
  "questions": {
    "department": {"type": "choice", "instructions": "Which department should handle this?",
      "criteria": {"billing": "invoices, payments, refunds", "technical": "bugs, outages", "other": "everything else"}},
    "urgency": {"type": "score", "instructions": "How urgent is this?", "criteria": ["not urgent", "soon", "critical"]},
    "churn": {"type": "noul", "instructions": "Does the user threaten to cancel?"}}}'

curl -X POST http://<HOST>:8100/v1/entail -H 'Content-Type: application/json' -d '{
  "premise": "The cat sat on the mat.", "hypotheses": ["A cat is on a mat.", "A dog is running."]}'
# {"entailment":[0.9978,0.0002], ...}
```

Response: `{"model", "probability_method": "normalized_entailment_v1", "answers": {id: {...}}}`.
Probabilities are the per-option entailment probability normalised over options; calibration is not guaranteed.

## laya (:8200)

| Endpoint | Purpose |
|---|---|
| `GET /health` | loaded checkpoints, device |
| `POST /v1/systemone` | typed decisions for one text |
| `POST /v1/systemone/batch` | same `questions` for many `states` |
| `POST /v1/route` | which checkpoint would answer (no inference); `explain: true` for reasoning |

Optional body fields: `model` (`english` / `multilingual` / `typed-decisions`), `lang`, `lang_guess`, `max_len`, `min_confidence`.

```bash
curl -X POST http://<HOST>:8200/v1/systemone/batch -H 'Content-Type: application/json' -d '{
  "states": ["Billed twice, refund please.", "The app crashes on the settings page."],
  "questions": {"department": {"type": "choice", "instructions": "Which department?",
    "criteria": {"billing": "payments", "technical": "bugs", "other": "else"}}}}'
```

Response adds `usage`, `answer_confidence`, `x_jev_confidence` and routing info. laya's own Swagger has no request schema;
`laya_app.py` injects examples into the OpenAPI document so `/docs` works with Try it out.

## Python

```python
import requests
r = requests.post("http://<HOST>:8100/v1/systemone", json={
    "state": "Refunds need a receipt. The customer has none.",
    "questions": {"ok": {"type": "noul", "instructions": "Is a refund permitted?"}}})
print(r.json()["answers"]["ok"]["noul"])
```

Browser JavaScript can call both servers directly (CORS `*` is enabled). With `USE_KEYS=1` add `Authorization: Bearer <key>`.
