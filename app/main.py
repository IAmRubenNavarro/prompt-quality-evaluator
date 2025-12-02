from fastapi import FastAPI
from app.services.evaluator import EvaluatorService

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/evaluate")
def evalute(user_prompt: str):
    svc = EvaluatorService()
    result = svc.evaluate(user_prompt)
    return result