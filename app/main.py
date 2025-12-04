from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.evaluator import EvaluatorService
from app.services.rewriter import RewriterService
from app.services.grader import GraderService

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class PromptRequest(BaseModel):
    user_prompt: str

class GradeRequest(BaseModel):
    expected: str
    actual: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/evaluate")
def evaluate(request: PromptRequest):
    svc = EvaluatorService()
    result = svc.evaluate(request.user_prompt)
    return result

@app.post("/rewrite")
def rewrite(request: PromptRequest):
    svc = RewriterService()
    result = svc.rewrite(request.user_prompt)
    return {"rewritten_prompt": result}

@app.post("/grade")
def grade(request: GradeRequest):
    svc = GraderService()
    result = svc.grade(request.expected, request.actual)
    return result