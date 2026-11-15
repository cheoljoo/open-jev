"""laya-serve app + CORS + a documented OpenAPI schema (request bodies with working examples)."""
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from laya.serve import create_app

app = create_app()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

QUESTIONS = {
    "department": {"type": "choice", "instructions": "Which department should handle this?",
                   "criteria": {"billing": "invoices, payments, refunds",
                                "technical": "bugs, outages, system errors",
                                "other": "everything else"}},
    "urgency": {"type": "score", "instructions": "How urgent is this?",
                "criteria": ["not urgent", "soon", "blocking"]},
    "churn_risk": {"type": "noul", "instructions": "Does the user threaten to cancel or leave?"},
}
STATE = "Hi, we were billed twice for March. Please refund the duplicate today or we will cancel our plan."

DOCS = {
    "/v1/systemone": ("Typed decisions for one text",
        "`questions` is `{id: {type, instructions, criteria}}`. **choice**: criteria = `{label: rubric}` (2+ options). "
        "**score**: criteria = `[labels low->high]`. **noul**: yes/no, no criteria. Optional: `model` "
        "(english | multilingual | typed-decisions), `lang`, `max_len`, `min_confidence`.",
        {"state": STATE, "questions": QUESTIONS}),
    "/v1/systemone/batch": ("Typed decisions for many texts",
        "Same `questions` for every entry of `states`. Optional `batch_size`, `sort_by_length`.",
        {"states": [STATE, "The app crashes every time I open the settings page.",
                    "Thanks, the invoice looks right now."], "questions": QUESTIONS}),
    "/v1/route": ("Show which checkpoint would answer (no inference)",
        "Returns the routing decision only. Set `explain: true` for the reasoning.",
        {"state": STATE, "questions": QUESTIONS, "explain": True}),
}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title="Laya API", version="1.0",
                         description="Multilingual typed-decision engine (laya). Same wire format as /v1/systemone of Jev.",
                         routes=app.routes)
    for path, (summary, desc, example) in DOCS.items():
        op = schema["paths"][path]["post"]
        op["summary"], op["description"] = summary, desc
        op["requestBody"] = {"required": True, "content": {"application/json": {
            "schema": {"type": "object", "example": example}, "example": example}}}
        op["parameters"] = [p for p in op.get("parameters", []) if p.get("name") != "authorization"]
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
