from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from app.routers import podcast
import os

app = FastAPI(
    title="Keyword to Podcast API",
    description="API for generating podcasts from keywords with flexible content generation",
    version="1.0.0"
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Configure with your domains in production

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# Mount the output directory for serving static files with caching headers
app.mount("/output", StaticFiles(
    directory="output",
    html=True,  # Allow HTML files if needed
    check_dir=True  # Verify directory exists
), name="output")

# Include routers
app.include_router(podcast.router)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Keyword to Podcast API</title>
        </head>
        <body>
            <h1>Keyword to Podcast API</h1>
            <p>Status: Active</p>
            <p>Access audio files at: /output/[filename]</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8088,
        reload=True,
        access_log=True
    ) 