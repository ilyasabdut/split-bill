"""
Main FastAPI application with modular router structure.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from .routers import health, receipts, splits

# Create FastAPI app
app = FastAPI(
    title="Bill Splitter API",
    description="API for uploading receipts, extracting data, and calculating bill splits.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(receipts.router)
app.include_router(splits.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Bill Splitter API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler."""
    return {
        "error": {
            "type": "HTTPException",
            "status_code": exc.status_code,
            "detail": exc.detail,
        }
    }


# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler for unexpected errors."""
    return {
        "error": {
            "type": "InternalServerError",
            "status_code": 500,
            "detail": "An unexpected error occurred",
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
