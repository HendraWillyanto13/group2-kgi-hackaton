from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.routes import health, upload, detection, pdf_embeddings

# Create FastAPI instance
app = FastAPI(
    title="FastAPI Backend Service",
    description="A FastAPI backend service with health check and file upload endpoints",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(detection.router, prefix="/api", tags=["Detection"])
app.include_router(pdf_embeddings.router, prefix="/api", tags=["PDF Embeddings"])

# Mount static files for uploaded images
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Mount static files for processed PDF documents
DOCUMENTS_DIR = Path("documents")
DOCUMENTS_DIR.mkdir(exist_ok=True)
app.mount("/documents", StaticFiles(directory=str(DOCUMENTS_DIR)), name="documents")

# Mount the uploads-metadata.json file directly
from fastapi import Response
import json

@app.get("/uploads-metadata.json")
async def get_uploads_metadata():
    """Serve the uploads metadata JSON file."""
    try:
        metadata_file = Path("uploads-metadata.json")
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            return metadata
        else:
            return {"uploads": []}
    except Exception as e:
        return {"uploads": [], "error": str(e)}

@app.get("/")
async def root():
    """Root endpoint that returns a welcome message."""
    return {
        "message": "Welcome to FastAPI Backend Service", 
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }