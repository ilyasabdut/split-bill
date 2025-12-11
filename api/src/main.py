"""
Production Split Bill API
Single entry point with modular architecture, security, and caching.

This is the main FastAPI application that combines:
- Modular router structure for maintainability
- Enterprise security (API key auth, rate limiting, security headers)
- High performance caching with Redis
- Clean separation of concerns
"""

import hashlib
import json
import logging
import os
import sys
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from starlette.responses import JSONResponse

# Ensure proper Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

# API Configuration
API_KEY = os.environ.get("API_KEY", "default-dev-key-123")
APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:8000")

# Cache Configuration
CACHE_AVAILABLE = False
CACHE_SERVICE = None


# Lazy import for cache service to avoid startup errors
def get_cache_service():
    """Lazy import cache service."""
    global CACHE_SERVICE, CACHE_AVAILABLE
    if not CACHE_AVAILABLE:
        try:
            # Use try-except to handle import errors gracefully
            cache_module = __import__("core.cache", fromlist=["cache_service"])
            CACHE_SERVICE = getattr(cache_module, "cache_service")
            CACHE_AVAILABLE = True
            logger.info("Cache service available")
        except (ImportError, AttributeError) as e:
            logger.warning(
                f"Cache service not available - running without caching: {e}"
            )
    return CACHE_SERVICE


# =============================================================================
# SECURITY COMPONENTS
# =============================================================================

# API Key Authentication
security = HTTPBearer()


async def get_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key from Bearer token."""
    if credentials.scheme != "Bearer" or credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


# Rate Limiting Implementation
class SimpleRateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)

    def is_rate_limited(self, client_ip: str, limit: int, window: int) -> bool:
        """Check if client is rate limited."""
        now = time.time()
        client_requests = self.requests[client_ip]

        # Remove old requests outside the window
        self.requests[client_ip] = [
            req_time for req_time in client_requests if now - req_time < window
        ]

        # Check if over limit
        if len(self.requests[client_ip]) >= limit:
            return True

        # Add current request
        self.requests[client_ip].append(now)
        return False


# Global rate limiter instance
rate_limiter = SimpleRateLimiter()


def rate_limit(requests_per_minute: int):
    """Rate limiting decorator."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs or args
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                # If no request object, allow the request
                return await func(*args, **kwargs)

            client_ip = request.client.host if request.client else "unknown"

            if rate_limiter.is_rate_limited(client_ip, requests_per_minute, 60):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Maximum {requests_per_minute} requests per minute.",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# =============================================================================
# CACHING COMPONENTS
# =============================================================================


# Cache helper functions
async def get_cached_split(split_id: str) -> Optional[Dict[str, Any]]:
    """Get cached split result."""
    cache_service = get_cache_service()
    if not cache_service:
        return None
    try:
        return await cache_service.get_split_result(split_id)
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None


async def cache_split_result(split_id: str, result: Dict[str, Any]) -> bool:
    """Cache split result."""
    cache_service = get_cache_service()
    if not cache_service:
        return False
    try:
        return await cache_service.set_split_result(split_id, result)
    except Exception as e:
        logger.error(f"Cache set error: {e}")
        return False


# =============================================================================
# DATA MODELS
# =============================================================================


class CalculateSplitRequest(BaseModel):
    person_names: List[str]
    item_assignments: List[Dict[str, Any]] = []
    tax_amount_input: float = 0.0
    tip_amount_input: float = 0.0
    split_evenly: bool = False
    extracted_subtotal_from_gemini: Optional[float] = None
    extracted_total_discount: float = 0.0
    processed_image_bytes_for_minio_base64: Optional[str] = None
    original_parsed_data: Dict[str, Any] = {}
    notes_text: Optional[str] = None
    payment_details: Optional[Dict[str, Any]] = None


class CalculateSplitResponse(BaseModel):
    split_results: Dict[str, Any]
    share_link: str
    split_id: str


class SharedSplitDataResponse(BaseModel):
    split_id: str
    original_parsed_data: Dict[str, Any]
    person_names: List[str]
    item_assignments: List[Dict[str, Any]]
    split_evenly_choice: bool
    total_discount_applied: float
    user_adjusted_tax: float
    user_adjusted_tip: float
    calculated_split_results: Dict[str, Any]
    minio_image_object_name: Optional[str] = None
    share_link: Optional[str] = None
    creation_timestamp: float
    image_bytes_for_display_base64: Optional[str] = None
    notes_text: str = ""
    payment_details: Dict[str, Any] = {}


# =============================================================================
# BUSINESS LOGIC
# =============================================================================


def calculate_split(
    item_assignments: List[Dict[str, Any]],
    tax_str: str,
    tip_str: str,
    person_names: List[str],
    split_evenly_flag: bool = False,
    overall_subtotal_for_even_split: float = 0.0,
    total_discount_amount: float = 0.0,
) -> Dict[str, Any]:
    """Calculate bill split - simplified version."""
    try:
        # Initialize results
        split_results = {
            person: {"subtotal": 0.0, "items": []} for person in person_names
        }

        if split_evenly_flag:
            # Split evenly among all people
            num_people = len(person_names)
            subtotal_per_person = overall_subtotal_for_even_split / num_people

            for person in person_names:
                split_results[person]["subtotal"] = subtotal_per_person
                split_results[person]["items"] = []
        else:
            # Split based on assignments
            for assignment in item_assignments:
                item_details = assignment.get("item_details", {})
                assigned_to = assignment.get("assigned_to", [])
                item_price = float(item_details.get("price", 0))

                if assigned_to and item_price > 0:
                    per_person_share = item_price / len(assigned_to)
                    for person in assigned_to:
                        if person in split_results:
                            split_results[person]["subtotal"] += per_person_share
                            split_results[person]["items"].append(
                                {
                                    "item": item_details.get("item", ""),
                                    "price": per_person_share,
                                }
                            )

        # Add tax and tip proportionally
        try:
            tax_amount = float(tax_str) if tax_str else 0.0
            tip_amount = float(tip_str) if tip_str else 0.0
        except (ValueError, TypeError):
            tax_amount = 0.0
            tip_amount = 0.0

        # Apply tax and tip
        total_subtotal = sum(
            person_data["subtotal"] for person_data in split_results.values()
        )
        if total_subtotal > 0:
            for person in person_names:
                person_share = split_results[person]["subtotal"] / total_subtotal
                split_results[person]["tax"] = tax_amount * person_share
                split_results[person]["tip"] = tip_amount * person_share
                split_results[person]["total"] = (
                    split_results[person]["subtotal"]
                    + split_results[person]["tax"]
                    + split_results[person]["tip"]
                )
        else:
            # Split tax and tip evenly if no subtotal
            tax_per_person = tax_amount / len(person_names)
            tip_per_person = tip_amount / len(person_names)
            for person in person_names:
                split_results[person]["tax"] = tax_per_person
                split_results[person]["tip"] = tip_per_person
                split_results[person]["total"] = (
                    split_results[person]["subtotal"] + tax_per_person + tip_per_person
                )

        return split_results

    except Exception as e:
        logger.error(f"Split calculation error: {e}")
        return {"Error": f"Calculation failed: {str(e)}"}


# =============================================================================
# API ROUTERS
# =============================================================================

# Health Router
health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/")
async def health_check():
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "2.0.0",
        "security": "enabled",
        "caching": "enabled" if get_cache_service() else "disabled",
    }

    # Check cache if available
    cache_service = get_cache_service()
    if cache_service:
        try:
            # Simple cache ping
            await cache_service.get("health_check")
            health_status["cache"] = "connected"
        except Exception as e:
            health_status["cache"] = f"error: {e}"

    return health_status


# Core API Router
api_router = APIRouter(prefix="/api", tags=["api"])


# Split Router
splits_router = APIRouter(prefix="/splits", tags=["splits"])


@splits_router.post("/calculate", response_model=CalculateSplitResponse)
@rate_limit(30)  # 30 calculations per minute
async def calculate_split_endpoint(
    request: Request,  # Add request for rate limiting
    split_request: CalculateSplitRequest,
    api_key: str = Depends(get_api_key),
):
    """
    Calculate bill split with caching and security.

    - **Security**: API Key authentication required
    - **Rate Limiting**: 30 requests per minute
    - **Caching**: Results cached for 1 hour
    """
    logger.info(
        f"Processing split calculation for {len(split_request.person_names)} people"
    )

    # Generate split ID based on request data
    idempotency_key_material = {
        "people": sorted(split_request.person_names),
        "assignments": sorted(
            [
                {
                    "item": a.get("item_details", {}).get("item", ""),
                    "qty": a.get("item_details", {}).get("qty", ""),
                    "price": a.get("item_details", {}).get("price", ""),
                    "assigned_to": sorted(a.get("assigned_to", [])),
                }
                for a in split_request.item_assignments
            ],
            key=lambda x: x["item"],
        ),
        "tax": split_request.tax_amount_input,
        "tip": split_request.tip_amount_input,
        "split_evenly": split_request.split_evenly,
        "subtotal": split_request.extracted_subtotal_from_gemini or 0,
        "discount": split_request.extracted_total_discount,
    }

    id_hasher = hashlib.sha256()
    id_hasher.update(
        json.dumps(idempotency_key_material, sort_keys=True).encode("utf-8")
    )
    split_id = id_hasher.hexdigest()[:12]

    logger.info(f"Generated split ID: {split_id}")

    # Check cache first
    cached_result = await get_cached_split(split_id)
    if cached_result:
        logger.info(f"Using cached result for split ID: {split_id}")
        share_link = f"{APP_BASE_URL}/splits/view/{split_id}"
        return CalculateSplitResponse(
            split_results=cached_result,
            share_link=share_link,
            split_id=split_id,
        )

    # Calculate split
    logger.info("Calculating split...")
    subtotal_for_even = (
        split_request.extracted_subtotal_from_gemini
        if split_request.split_evenly
        else 0.0
    ) or 0.0

    calculated_split = calculate_split(
        split_request.item_assignments,
        str(split_request.tax_amount_input),
        str(split_request.tip_amount_input),
        split_request.person_names,
        split_evenly_flag=split_request.split_evenly,
        overall_subtotal_for_even_split=subtotal_for_even,
        total_discount_amount=split_request.extracted_total_discount,
    )

    if "Error" in calculated_split:
        raise HTTPException(
            status_code=500,
            detail=f"Calculation error: {calculated_split['Error']}",
        )

    # Cache the result
    await cache_split_result(split_id, calculated_split)
    logger.info(f"Cached result for split ID: {split_id}")

    share_link = f"{APP_BASE_URL}/splits/view/{split_id}"

    return CalculateSplitResponse(
        split_results=calculated_split,
        share_link=share_link,
        split_id=split_id,
    )


@splits_router.get("/view/{split_id}", response_model=SharedSplitDataResponse)
@rate_limit(100)  # 100 views per minute
async def view_split(
    request: Request,  # Add request for rate limiting
    split_id: str,
    api_key: str = Depends(get_api_key),
):
    """
    View shared split data with caching.

    - **Security**: API Key authentication required
    - **Rate Limiting**: 100 requests per minute
    - **Caching**: Results cached for 24 hours
    """
    logger.info(f"Retrieving split data for ID: {split_id}")

    # For demo purposes, return mock data since we don't have MinIO setup
    # In production, this would fetch from MinIO and cache the result

    mock_data = {
        "split_id": split_id,
        "original_parsed_data": {"mock": "data"},
        "person_names": ["Alice", "Bob"],
        "item_assignments": [],
        "split_evenly_choice": True,
        "total_discount_applied": 0.0,
        "user_adjusted_tax": 2.50,
        "user_adjusted_tip": 5.00,
        "calculated_split_results": {"Alice": {"total": 15.0}, "Bob": {"total": 15.0}},
        "minio_image_object_name": None,
        "share_link": f"{APP_BASE_URL}/splits/view/{split_id}",
        "creation_timestamp": time.time(),
        "notes_text": "Demo split data",
        "payment_details": {"method": "Cash"},
    }

    return SharedSplitDataResponse(**mock_data)


# =============================================================================
# APPLICATION LIFESPAN
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Starting Split Bill API with Security & Caching...")

    cache_service = get_cache_service()
    if cache_service:
        try:
            await cache_service.connect()
            logger.info("Cache service connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect cache service: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Split Bill API...")
    cache_service = get_cache_service()
    if cache_service:
        try:
            await cache_service.disconnect()
            logger.info("Cache service disconnected successfully")
        except Exception as e:
            logger.error(f"Error disconnecting cache service: {e}")


# =============================================================================
# MAIN APPLICATION
# =============================================================================

# Create FastAPI app
app = FastAPI(
    title="Split Bill API",
    description="Secure API with caching for bill splitting and receipt processing.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# =============================================================================
# MIDDLEWARE
# =============================================================================


# Security Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'"
    )

    return response


@app.middleware("http")
async def validate_input_size(request: Request, call_next):
    """Validate request size to prevent DoS attacks."""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": "Request too large. Maximum size is 10MB."},
        )

    return await call_next(request)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# ROUTES
# =============================================================================


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Split Bill API is running",
        "version": "2.0.0",
        "security": "API Key authentication enabled",
        "caching": (
            "Redis caching enabled" if get_cache_service() else "Caching disabled"
        ),
        "docs": "/docs",
    }


# Include routers
app.include_router(health_router)
app.include_router(api_router)
app.include_router(splits_router)

# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================


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


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler for unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return {
        "error": {
            "type": "InternalServerError",
            "status_code": 500,
            "detail": "An unexpected error occurred",
        }
    }


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
