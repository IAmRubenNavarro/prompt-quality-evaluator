from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, validator
from pathlib import Path
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import os

from app.services.evaluator import EvaluatorService
from app.services.rewriter import RewriterService
from app.services.grader import GraderService

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self' https://openrouter.ai https://*.azurecontainerapps.io; "
            "font-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Restrict CORS to specific origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=600,
)

# Custom error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid request data", "errors": exc.errors()},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log the error but don't expose internal details
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred"},
    )

# Request models with validation
class PromptRequest(BaseModel):
    user_prompt: str = Field(..., min_length=1, max_length=10000, description="User prompt to process")

    @validator('user_prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty or whitespace only')
        return v.strip()

class GradeRequest(BaseModel):
    expected: str = Field(..., min_length=1, max_length=10000, description="Expected prompt")
    actual: str = Field(..., min_length=1, max_length=10000, description="Actual prompt to grade")

    @validator('expected', 'actual')
    def validate_prompts(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty or whitespace only')
        return v.strip()

@app.get("/health")
@limiter.limit("60/minute")
def health(request: Request):
    return {"status": "ok"}

@app.get("/")
@limiter.limit("30/minute")
def read_root(request: Request):
    # Get the project root directory (parent of app directory)
    demo_path = Path(__file__).parent.parent / "demo.html"

    # Check if file exists and return error if not
    if not demo_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Demo page not found"
        )

    return FileResponse(demo_path)

@app.post("/evaluate")
@limiter.limit("10/minute")
def evaluate(request: Request, prompt_request: PromptRequest):
    try:
        svc = EvaluatorService()
        result = svc.evaluate(prompt_request.user_prompt)
        formatted_text = svc.format_evaluation(result)
        return {
            "formatted": formatted_text,
            "raw": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred processing your request")

@app.post("/rewrite")
@limiter.limit("10/minute")
def rewrite(request: Request, prompt_request: PromptRequest):
    try:
        svc = RewriterService()
        result = svc.rewrite(prompt_request.user_prompt)
        return {"rewritten_prompt": result}
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred processing your request")

@app.post("/grade")
@limiter.limit("10/minute")
def grade(request: Request, grade_request: GradeRequest):
    try:
        svc = GraderService()
        result = svc.grade(grade_request.expected, grade_request.actual)
        formatted_text = svc.format_grade(result)
        return {
            "formatted": formatted_text,
            "raw": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred processing your request")