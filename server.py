"""OpenJev HTTP API (typed decisions). Run: ./start.sh  ->  http://127.0.0.1:8100/docs"""
import math
import os
import sys
import threading
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "openjev" / "code"))

from fastapi import Depends, FastAPI, Header, HTTPException  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from openjev_decide import OpenJev  # noqa: E402

MODEL_DIR = os.environ.get("OPENJEV_MODEL", str(ROOT / "openjev" / "qwen3.5-4b-nli-v5"))
API_KEY = os.environ.get("OPENJEV_API_KEY")  # optional; if set, require "Authorization: Bearer <key>"
MODEL_NAME = "openjev/qwen3.5-4b-nli-v5"

app = FastAPI(title="OpenJev API", version="1.0")
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
_lock = threading.Lock()  # one GPU forward at a time
_jev: Optional[OpenJev] = None


@app.on_event("startup")
def _load():
    global _jev
    os.environ.setdefault("OPENJEV_DTYPE", "bfloat16")
    _jev = OpenJev.from_pretrained(MODEL_DIR, device=os.environ.get("OPENJEV_DEVICE", "cuda"))


def auth(authorization: Optional[str] = Header(None)):
    if API_KEY and authorization != f"Bearer {API_KEY}":
        raise HTTPException(401, "invalid or missing API key")


class Question(BaseModel):
    type: str = Field("choice", description="choice | score | noul")
    instructions: str
    criteria: Optional[Any] = Field(
        None, description="choice: {label: rubric}; score: [labels low->high]; noul: ignored")


class SystemOneRequest(BaseModel):
    state: Any = Field(..., description="the text (or JSON) to decide over")
    questions: dict[str, Question]
    model: Optional[str] = None

    model_config = {"json_schema_extra": {"example": {
        "state": "We were billed twice for March. Please refund it today.",
        "questions": {
            "department": {"type": "choice", "instructions": "Which department should handle this?",
                           "criteria": {"billing": "invoices, payments, refunds",
                                        "technical": "bugs, outages", "other": "everything else"}},
            "urgency": {"type": "score", "instructions": "How urgent is this?",
                        "criteria": ["not urgent", "soon", "critical"]},
            "churn": {"type": "noul", "instructions": "Does the user threaten to cancel?"},
        }}}}


def _spec(q: Question):
    """-> (options, rubric string appended to the instruction) for one question."""
    if q.type == "noul":
        return ["no", "yes"], q.instructions
    if q.type == "score":
        labels = [str(c) for c in (q.criteria or [])]
        if len(labels) < 2:
            raise HTTPException(422, "score needs criteria: a list of >=2 labels")
        return labels, q.instructions
    if not isinstance(q.criteria, dict) or len(q.criteria) < 2:
        raise HTTPException(422, "choice needs criteria: {label: rubric} with >=2 options")
    return list(q.criteria), q.instructions


def _run(state, questions: dict[str, Question]) -> dict:
    import json
    from openjev_decide import RUBRIC_MARK
    ids, qs = [], []
    for qid, q in questions.items():
        options, instr = _spec(q)
        if q.type == "choice":
            instr += RUBRIC_MARK + json.dumps({k: str(v) for k, v in q.criteria.items()})
        ids.append(qid)
        qs.append({"type": "noul" if q.type == "noul" else "choice", "instructions": instr, "options": options})
    with _lock:
        raw = _jev.decide(state, qs)
    answers = {}
    for qid, q, r in zip(ids, questions.values(), raw):
        if q.type == "noul":
            p = r["noul"]
            answers[qid] = {"noul": p, "answer": "yes" if p >= 0.5 else "no"}
            continue
        probs = r["probabilities"]
        top = max(probs, key=probs.get)
        ent = -sum(x * math.log(x) for x in probs.values() if x > 0) / math.log(len(probs))
        a = {"choice": top, "probabilities": probs, "confidence": 1 - ent}
        if q.type == "score":
            a["score"] = list(probs).index(top)
        answers[qid] = a
    return {"model": MODEL_NAME, "probability_method": "normalized_entailment_v1", "answers": answers}


@app.get("/health", summary="Server status")
def health():
    return {"status": "ok" if _jev else "loading", "model": MODEL_NAME}


@app.post("/v1/systemone", summary="Typed decisions (choice / score / noul)", dependencies=[Depends(auth)])
def systemone(req: SystemOneRequest):
    return _run(req.state, req.questions)


@app.post("/predict", summary="Alias of /v1/systemone", dependencies=[Depends(auth)])
def predict(req: SystemOneRequest):  # alias, same shape as laya-serve
    return _run(req.state, req.questions)


class NLIRequest(BaseModel):
    premise: str
    hypotheses: list[str]

    model_config = {"json_schema_extra": {"example": {
        "premise": "The cat sat on the mat.",
        "hypotheses": ["A cat is on a mat.", "A dog is running."]}}}


@app.post("/v1/entail", summary="P(entailment) of each hypothesis given a premise", dependencies=[Depends(auth)])
def entail(req: NLIRequest):
    """Raw P(entailment) of each hypothesis given the premise (reranking / grading / guarding)."""
    import numpy as np
    from modeling_openjev import ENT
    with _lock:
        p = _jev.ce.predict([(req.premise, h) for h in req.hypotheses])[:, ENT]
    return {"model": MODEL_NAME, "entailment": [float(x) for x in np.asarray(p)]}
