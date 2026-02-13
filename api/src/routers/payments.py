"""Payments router for the Split Bill API.

This module handles payment tracking and status updates.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.deps import get_db
from src.db.models import Payment, Split

logger = logging.getLogger(__name__)

payments_router = APIRouter(prefix="/payments", tags=["payments"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class PaymentCreate(BaseModel):
    """Request model for creating a payment."""

    split_id: int = Field(..., description="Associated split ID")
    person_name: str = Field(
        ..., min_length=1, max_length=255, description="Payer name"
    )
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field(..., min_length=3, max_length=10, description="Currency code")


class PaymentUpdate(BaseModel):
    """Request model for updating a payment."""

    status: Optional[str] = Field(
        None, description="Payment status: 'unpaid', 'paid', 'confirmed'"
    )


class PaymentResponse(BaseModel):
    """Response model for payment data."""

    id: int
    split_id: int
    person_name: str
    amount: float
    currency: str
    status: str
    confirmed_at: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# ENDPOINTS
# ============================================================================


@payments_router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
    request: Request,
    payment_data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
) -> PaymentResponse:
    """Create a new payment record.

    Args:
        request: FastAPI request object
        payment_data: Payment creation data
        db: Database session

    Returns:
        PaymentResponse with created payment details

    Raises:
        HTTPException: If split not found (404)
    """
    try:
        logger.info(
            f"Creating payment for split {payment_data.split_id}: "
            f"{payment_data.person_name} - {payment_data.amount} {payment_data.currency}"
        )

        # Verify split exists
        split_result = await db.execute(
            select(Split).where(Split.id == payment_data.split_id)
        )
        split = split_result.scalar_one_or_none()

        if not split:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Split with ID {payment_data.split_id} not found",
            )

        # Create payment
        payment = Payment(
            split_id=payment_data.split_id,
            person_name=payment_data.person_name,
            amount=payment_data.amount,
            currency=payment_data.currency,
            status="unpaid",
        )
        db.add(payment)
        await db.commit()
        await db.refresh(payment)

        logger.info(f"Payment created with ID: {payment.id}")
        return PaymentResponse(
            id=payment.id,
            split_id=payment.split_id,
            person_name=payment.person_name,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            confirmed_at=(
                payment.confirmed_at.isoformat() if payment.confirmed_at else None
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payment: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@payments_router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_payment(
    request: Request,
    payment_id: int,
    db: AsyncSession = Depends(get_db),
) -> PaymentResponse:
    """Get a payment by ID.

    Args:
        request: FastAPI request object
        payment_id: Payment ID
        db: Database session

    Returns:
        PaymentResponse with payment details

    Raises:
        HTTPException: If payment not found (404)
    """
    try:
        logger.info(f"Fetching payment: {payment_id}")

        result = await db.execute(select(Payment).where(Payment.id == payment_id))
        payment = result.scalar_one_or_none()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment with ID {payment_id} not found",
            )

        return PaymentResponse(
            id=payment.id,
            split_id=payment.split_id,
            person_name=payment.person_name,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            confirmed_at=(
                payment.confirmed_at.isoformat() if payment.confirmed_at else None
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching payment: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@payments_router.get(
    "/",
    response_model=List[PaymentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_payments(
    request: Request,
    split_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> List[PaymentResponse]:
    """List all payments, optionally filtered by split or status.

    Args:
        request: FastAPI request object
        split_id: Optional filter for split ID
        status: Optional filter for payment status
        db: Database session

    Returns:
        List of PaymentResponse objects
    """
    try:
        logger.info(f"Listing payments (split_id: {split_id}, status: {status})")

        query = select(Payment)
        if split_id is not None:
            query = query.where(Payment.split_id == split_id)
        if status is not None:
            query = query.where(Payment.status == status)

        result = await db.execute(query)
        payments = result.scalars().all()

        return [
            PaymentResponse(
                id=p.id,
                split_id=p.split_id,
                person_name=p.person_name,
                amount=p.amount,
                currency=p.currency,
                status=p.status,
                confirmed_at=p.confirmed_at.isoformat() if p.confirmed_at else None,
            )
            for p in payments
        ]

    except Exception as e:
        logger.error(f"Error listing payments: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@payments_router.put(
    "/{payment_id}",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
)
async def update_payment(
    request: Request,
    payment_id: int,
    payment_data: PaymentUpdate,
    db: AsyncSession = Depends(get_db),
) -> PaymentResponse:
    """Update a payment status.

    Args:
        request: FastAPI request object
        payment_id: Payment ID
        payment_data: Payment update data
        db: Database session

    Returns:
        PaymentResponse with updated payment details

    Raises:
        HTTPException: If payment not found (404)
    """
    try:
        logger.info(f"Updating payment: {payment_id}")

        result = await db.execute(select(Payment).where(Payment.id == payment_id))
        payment = result.scalar_one_or_none()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment with ID {payment_id} not found",
            )

        if payment_data.status is not None:
            payment.status = payment_data.status
            # Set confirmed_at if status is confirmed
            if payment_data.status == "confirmed" and payment.confirmed_at is None:
                payment.confirmed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(payment)

        return PaymentResponse(
            id=payment.id,
            split_id=payment.split_id,
            person_name=payment.person_name,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status,
            confirmed_at=(
                payment.confirmed_at.isoformat() if payment.confirmed_at else None
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating payment: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@payments_router.delete(
    "/{payment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_payment(
    request: Request,
    payment_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a payment.

    Args:
        request: FastAPI request object
        payment_id: Payment ID
        db: Database session

    Raises:
        HTTPException: If payment not found (404)
    """
    try:
        logger.info(f"Deleting payment: {payment_id}")

        result = await db.execute(select(Payment).where(Payment.id == payment_id))
        payment = result.scalar_one_or_none()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment with ID {payment_id} not found",
            )

        await db.delete(payment)
        await db.commit()

        logger.info(f"Payment deleted: {payment_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting payment: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@payments_router.get(
    "/split/{split_id}/summary",
    status_code=status.HTTP_200_OK,
)
async def get_split_payment_summary(
    request: Request,
    split_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get payment summary for a split.

    Args:
        request: FastAPI request object
        split_id: Split ID
        db: Database session

    Returns:
        Dict with payment summary statistics

    Raises:
        HTTPException: If split not found (404)
    """
    try:
        logger.info(f"Getting payment summary for split: {split_id}")

        # Verify split exists
        split_result = await db.execute(select(Split).where(Split.id == split_id))
        split = split_result.scalar_one_or_none()

        if not split:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Split with ID {split_id} not found",
            )

        # Get all payments for split
        result = await db.execute(select(Payment).where(Payment.split_id == split_id))
        payments = result.scalars().all()

        total_amount = sum(p.amount for p in payments)
        paid_amount = sum(p.amount for p in payments if p.status == "paid")
        confirmed_amount = sum(p.amount for p in payments if p.status == "confirmed")
        unpaid_count = sum(1 for p in payments if p.status == "unpaid")

        return {
            "split_id": split_id,
            "total_payments": len(payments),
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "confirmed_amount": confirmed_amount,
            "unpaid_count": unpaid_count,
            "completion_rate": (
                round(confirmed_amount / total_amount * 100, 2)
                if total_amount > 0
                else 0
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
