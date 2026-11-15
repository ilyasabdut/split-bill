"""
Split Bill API: single entry point.
"""

import base64
import logging
import os
import time
import uuid
from collections import defaultdict
from functools import wraps
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    File,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.deps import get_api_key, get_current_user, get_db, get_optional_user
from src.db.models import Split, User
from src.routers.analytics import analytics_router
from src.routers.currency import currency_router
from src.routers.groups import groups_router
from src.routers.payments import payments_router
from src.routers.templates import templates_router
from src.services.image_service import compress_image
from src.services.openrouter_ocr import extract_receipt_data_async
from starlette.responses import JSONResponse

load_dotenv()

logger = logging.getLogger(__name__)

# API Configuration
API_KEY = os.environ.get("API_KEY", "default-dev-key-123")
APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:8000")

# =============================================================================
# SECURITY COMPONENTS
# =============================================================================


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
# DATA MODELS
# =============================================================================


class ClientPersonResult(BaseModel):
    model_config = ConfigDict(extra="allow")
    total: float = Field(ge=0)


class CalculateSplitRequest(BaseModel):
    person_names: List[str]
    item_assignments: List[Dict[str, Any]] = []
    tax_amount_input: float = 0.0
    tip_amount_input: float = 0.0
    split_evenly: bool = False
    extracted_subtotal_from_gemini: Optional[float] = None
    extracted_total_discount: float = 0.0
    # The web app does the math (rounding, % and by-item modes) on the device;
    # when it sends its results the share link shows exactly those numbers.
    client_results: Optional[Dict[str, ClientPersonResult]] = None


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
    creation_timestamp: float
    payments: Dict[str, str] = {}


class PaidRequest(BaseModel):
    paid: bool


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
    """Calculate bill split."""
    try:
        split_results = {
            person: {"subtotal": 0.0, "items": []} for person in person_names
        }

        if split_evenly_flag:
            num_people = len(person_names)
            subtotal_per_person = (
                overall_subtotal_for_even_split / num_people if num_people > 0 else 0.0
            )

            for person in person_names:
                split_results[person]["subtotal"] = subtotal_per_person
                split_results[person]["items"] = []
        else:
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
            tax_per_person = (
                tax_amount / len(person_names) if len(person_names) > 0 else 0.0
            )
            tip_per_person = (
                tip_amount / len(person_names) if len(person_names) > 0 else 0.0
            )
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

health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/")
async def health_check():
    return {"status": "healthy"}


splits_router = APIRouter(prefix="/splits", tags=["splits"])
receipts_router = APIRouter(prefix="/receipts", tags=["receipts"])


@splits_router.post("/calculate", response_model=CalculateSplitResponse)
@rate_limit(30)
async def calculate_split_endpoint(
    request: Request,
    split_request: CalculateSplitRequest,
    api_key: str = Depends(get_api_key),
    user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """Calculate a bill split and persist it behind an unguessable share id."""
    if split_request.client_results is not None:
        if set(split_request.client_results) != set(split_request.person_names):
            raise HTTPException(
                status_code=422, detail="client_results must have one entry per person"
            )
        calculated_split = {
            name: result.model_dump()
            for name, result in split_request.client_results.items()
        }
    else:
        calculated_split = calculate_split(
            split_request.item_assignments,
            str(split_request.tax_amount_input),
            str(split_request.tip_amount_input),
            split_request.person_names,
            split_evenly_flag=split_request.split_evenly,
            overall_subtotal_for_even_split=split_request.extracted_subtotal_from_gemini
            or 0.0,
            total_discount_amount=split_request.extracted_total_discount,
        )
        if "Error" in calculated_split:
            raise HTTPException(
                status_code=500,
                detail=f"Calculation error: {calculated_split['Error']}",
            )

    split_id = uuid.uuid4().hex
    db.add(
        Split(
            share_id=split_id,
            owner_id=user.id if user else None,
            receipt_data=split_request.model_dump(exclude={"client_results"}),
            split_results=calculated_split,
        )
    )
    await db.commit()

    return CalculateSplitResponse(
        split_results=calculated_split,
        share_link=f"{APP_BASE_URL}/split/{split_id}",
        split_id=split_id,
    )


# Public share link: no API key, the uuid4 id is the capability.
@splits_router.get("/view/{split_id}", response_model=SharedSplitDataResponse)
@rate_limit(100)
async def view_split(
    request: Request,
    split_id: str,
    db: AsyncSession = Depends(get_db),
):
    split = await db.scalar(select(Split).where(Split.share_id == split_id))
    if split is None:
        raise HTTPException(status_code=404, detail="Split not found")

    req = split.receipt_data
    return SharedSplitDataResponse(
        split_id=split.share_id,
        original_parsed_data={},
        person_names=req["person_names"],
        item_assignments=req["item_assignments"],
        split_evenly_choice=req["split_evenly"],
        total_discount_applied=req["extracted_total_discount"],
        user_adjusted_tax=req["tax_amount_input"],
        user_adjusted_tip=req["tip_amount_input"],
        calculated_split_results=split.split_results,
        creation_timestamp=split.created_at.timestamp(),
        payments=split.paid_status or {},
    )


@splits_router.put("/{split_id}/payments/{person_name}")
async def set_paid(
    split_id: str,
    person_name: str,
    body: PaidRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Owner marks one person on their split as paid or unpaid."""
    split = await db.scalar(
        select(Split).where(Split.share_id == split_id, Split.owner_id == user.id)
    )
    if split is None:
        raise HTTPException(status_code=404, detail="Split not found")
    if person_name not in split.receipt_data["person_names"]:
        raise HTTPException(status_code=422, detail="Unknown person")
    # new dict so SQLAlchemy sees the JSON change
    paid = {k: v for k, v in (split.paid_status or {}).items() if k != person_name}
    if body.paid:
        paid[person_name] = "paid"
    split.paid_status = paid
    await db.commit()
    return {"split_id": split_id, "payments": paid}


@receipts_router.post("/upload")
@rate_limit(30)
async def upload_receipt(
    request: Request,
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key),
):
    """Upload a receipt image, process it with OCR, and return extracted data."""
    try:
        logger.info(f"Processing receipt upload: {file.filename}")

        # Read file content
        image_bytes = await file.read()

        # Compress the image before sending it to OCR
        compressed_image_bytes = compress_image(image_bytes)

        # Validate compression result before proceeding
        if compressed_image_bytes is None:
            logger.error(f"Failed to compress image: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail="Failed to process image. Please ensure it's a valid image file (JPEG, PNG, WEBP).",
            )

        # Perform OCR
        parsed_data = await extract_receipt_data_async(compressed_image_bytes)

        if "Error" in parsed_data:
            error_msg = parsed_data.get("message", "OCR processing failed")
            logger.error(f"OCR processing error: {error_msg}")
            raise HTTPException(status_code=400, detail=parsed_data)

        # The base64 of the processed image is needed for display and MinIO upload in the frontend
        processed_image_bytes_base64 = base64.b64encode(compressed_image_bytes).decode(
            "utf-8"
        )

        return {
            "parsed_data": parsed_data,
            "processed_image_bytes_base64": processed_image_bytes_base64,
            "extracted_subtotal_from_gemini": parsed_data.get("subtotal"),
            "extracted_total_discount": sum(
                d.get("amount", 0) for d in parsed_data.get("discounts", [])
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing receipt: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


app = FastAPI(
    title="Split Bill API",
    description="Bill splitting and receipt processing.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# =============================================================================
# MIDDLEWARE
# =============================================================================


@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)

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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(splits_router)
app.include_router(receipts_router)
app.include_router(currency_router)
app.include_router(groups_router)
app.include_router(templates_router)
app.include_router(payments_router)
app.include_router(analytics_router)

# =============================================================================
# ROUTES
# =============================================================================


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Split Bill API is running",
        "version": "2.0.0",
        "docs": "/docs",
    }


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "status_code": exc.status_code,
                "detail": exc.detail,
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler for unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "InternalServerError",
                "status_code": 500,
                "detail": "An unexpected error occurred",
            }
        },
    )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
