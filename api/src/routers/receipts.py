"""Receipt processing router for the Split Bill API.

This module handles receipt upload and OCR processing endpoints.
"""

import base64
import logging

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from src.dependencies import get_api_key, rate_limit
from src.models.schemas import ReceiptUploadResponse

logger = logging.getLogger(__name__)

receipts_router = APIRouter(prefix="/receipts", tags=["receipts"])


@receipts_router.post(
    "/upload",
    response_model=ReceiptUploadResponse,
    status_code=status.HTTP_200_OK,
)
@rate_limit(10)
async def upload_receipt(
    request: Request,
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key),
) -> ReceiptUploadResponse:
    """Upload a receipt image, process it with OCR, and return extracted data.

    This endpoint:
    1. Accepts a receipt image file (JPEG, PNG, WEBP)
    2. Compresses the image for efficient processing
    3. Sends to OpenRouter for OCR processing
    4. Returns structured receipt data

    Args:
        request: FastAPI request object
        file: Uploaded image file
        api_key: Authenticated API key

    Returns:
        ReceiptUploadResponse containing parsed data and processed image

    Raises:
        HTTPException: If processing fails (400, 500)
    """
    from services.image_service import compress_image
    from services.openrouter_ocr import extract_receipt_data

    try:
        logger.info(f"Processing receipt upload: {file.filename}")

        # Read file content
        image_bytes = await file.read()

        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Please upload an image file (JPEG, PNG, WEBP).",
            )

        # Validate file size
        max_size = 10 * 1024 * 1024  # 10MB
        if len(image_bytes) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large. Maximum size is 10MB.",
            )

        # Compress the image before sending it to OCR
        compressed_image_bytes = compress_image(image_bytes)

        # Handle compression failure
        if compressed_image_bytes is None:
            logger.error(f"Failed to compress image: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process image. Please ensure it's a valid image file.",
            )

        # Perform OCR
        parsed_data = extract_receipt_data(compressed_image_bytes)

        # Handle OCR errors
        if isinstance(parsed_data, dict) and "Error" in parsed_data:
            error_msg = parsed_data.get("message", "OCR processing failed")
            logger.error(f"OCR processing error: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=parsed_data,
            )

        # Encode compressed image for frontend
        processed_image_bytes_base64 = base64.b64encode(compressed_image_bytes).decode(
            "utf-8"
        )

        logger.info(f"Successfully processed receipt: {file.filename}")

        return ReceiptUploadResponse(
            parsed_data=parsed_data,
            processed_image_bytes_base64=processed_image_bytes_base64,
            extracted_subtotal_from_gemini=parsed_data.get("subtotal"),
            extracted_total_discount=sum(
                d.get("amount", 0) for d in parsed_data.get("discounts", [])
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing receipt: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
