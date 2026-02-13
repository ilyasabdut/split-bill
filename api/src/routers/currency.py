"""Currency router for the Split Bill API.

This module handles currency exchange rate and conversion endpoints.
"""

import logging

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field
from src.services.currency_service import currency_service

logger = logging.getLogger(__name__)

currency_router = APIRouter(prefix="/currency", tags=["currency"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class RateRequest(BaseModel):
    """Request model for getting exchange rate."""

    from_currency: str = Field(
        ..., min_length=3, max_length=3, description="Source currency code"
    )
    to_currency: str = Field(
        ..., min_length=3, max_length=3, description="Target currency code"
    )


class RateResponse(BaseModel):
    """Response model for exchange rate."""

    from_currency: str
    to_currency: str
    rate: float
    cached: bool = False


class ConvertRequest(BaseModel):
    """Request model for currency conversion."""

    amount: float = Field(..., gt=0, description="Amount to convert")
    from_currency: str = Field(
        ..., min_length=3, max_length=3, description="Source currency code"
    )
    to_currency: str = Field(
        ..., min_length=3, max_length=3, description="Target currency code"
    )


class ConvertResponse(BaseModel):
    """Response model for currency conversion."""

    original_amount: float
    original_currency: str
    converted_amount: float
    target_currency: str
    rate: float


# ============================================================================
# ENDPOINTS
# ============================================================================


@currency_router.get(
    "/rates",
    response_model=RateResponse,
    status_code=status.HTTP_200_OK,
)
async def get_exchange_rate(
    request: Request,
    from_currency: str,
    to_currency: str,
) -> RateResponse:
    """Get exchange rate between two currencies.

    Args:
        request: FastAPI request object
        from_currency: Source currency code (e.g., "USD", "IDR")
        to_currency: Target currency code (e.g., "USD", "IDR")

    Returns:
        RateResponse with exchange rate

    Raises:
        HTTPException: If rate unavailable (404)
    """
    try:
        logger.info(f"Fetching exchange rate: {from_currency} -> {to_currency}")

        rate = await currency_service.get_rate(from_currency, to_currency)

        if rate is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exchange rate unavailable for {from_currency} -> {to_currency}",
            )

        return RateResponse(
            from_currency=from_currency.upper(),
            to_currency=to_currency.upper(),
            rate=rate,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting exchange rate: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@currency_router.post(
    "/convert",
    response_model=ConvertResponse,
    status_code=status.HTTP_200_OK,
)
async def convert_currency(
    request: Request,
    convert_request: ConvertRequest,
) -> ConvertResponse:
    """Convert amount between currencies.

    Args:
        request: FastAPI request object
        convert_request: Conversion request with amount and currencies

    Returns:
        ConvertResponse with converted amount

    Raises:
        HTTPException: If conversion fails (400, 404)
    """
    try:
        logger.info(
            f"Converting {convert_request.amount} {convert_request.from_currency} "
            f"to {convert_request.to_currency}"
        )

        converted_amount = await currency_service.convert(
            convert_request.amount,
            convert_request.from_currency,
            convert_request.to_currency,
        )

        if converted_amount is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversion unavailable for {convert_request.from_currency} -> {convert_request.to_currency}",
            )

        # Get rate for response
        rate = await currency_service.get_rate(
            convert_request.from_currency,
            convert_request.to_currency,
        )

        return ConvertResponse(
            original_amount=convert_request.amount,
            original_currency=convert_request.from_currency.upper(),
            converted_amount=converted_amount,
            target_currency=convert_request.to_currency.upper(),
            rate=rate or 1.0,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting currency: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
