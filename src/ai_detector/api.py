"""
FastAPI Server & REST API for AI Text Detector
Authored by Arvind (https://github.com/Arvind208)
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .engine import analyze_text
from .samples import AI_SAMPLE_TEXT, HUMAN_SAMPLE_TEXT, MIXED_SAMPLE_TEXT


app = FastAPI(
    title="AI Sentinel - AI Text Detection API",
    description="High-performance AI vs. Human text classifier by Arvind (@Arvind208)",
    version="1.0.0",
)

# Enable CORS for developer ease
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent / "static"


class DetectionRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The raw text to evaluate")


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Sentinel Detector API",
        "author": "Arvind (https://github.com/Arvind208)",
        "version": "1.0.0"
    }


@app.get("/api/samples")
def get_sample_texts():
    """Returns sample human, AI, and mixed texts for quick demonstrations."""
    return {
        "ai": AI_SAMPLE_TEXT,
        "human": HUMAN_SAMPLE_TEXT,
        "mixed": MIXED_SAMPLE_TEXT
    }


@app.post("/api/detect")
def detect_text(payload: DetectionRequest):
    """Analyze provided text and return AI probability, metrics, and sentence breakdown."""
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text field cannot be empty.")
    
    result = analyze_text(payload.text)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result


# Mount static web directory if it exists
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(STATIC_DIR / "index.html")
