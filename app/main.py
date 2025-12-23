from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path

from app.services.evaluator import EvaluatorService
from app.services.rewriter import RewriterService
from app.services.grader import GraderService

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo purposes
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

@app.get("/debug")
def debug():
    import os
    current_file = Path(__file__)
    parent_dir = current_file.parent.parent

    files_in_parent = []
    if parent_dir.exists():
        files_in_parent = [str(f) for f in parent_dir.iterdir()]

    return {
        "current_file": str(current_file),
        "parent_dir": str(parent_dir),
        "demo_path": str(parent_dir / "demo.html"),
        "demo_exists": (parent_dir / "demo.html").exists(),
        "files_in_parent": files_in_parent,
        "cwd": os.getcwd()
    }

@app.get("/")
def read_root():
    # Get the project root directory (parent of app directory)
    demo_path = Path(__file__).parent.parent / "demo.html"

    # Check if file exists and return error if not
    if not demo_path.exists():
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail=f"demo.html not found at {demo_path}. File exists: {demo_path.exists()}"
        )

    return FileResponse(demo_path)

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