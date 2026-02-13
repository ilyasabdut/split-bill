"""Analytics router for the Split Bill API.

This module provides usage statistics and analytics endpoints.
"""

import logging
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.deps import get_db
from src.db.models import Payment, Split, User

logger = logging.getLogger(__name__)

analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class UserStatsResponse(BaseModel):
    """Response model for user statistics."""

    user_id: int
    total_splits: int
    total_amount: float
    splits_this_month: int
    avg_split_amount: float


class OverallStatsResponse(BaseModel):
    """Response model for overall application statistics."""

    total_users: int
    total_splits: int
    total_payments: int
    total_amount_processed: float
    active_users_this_month: int


class CurrencyUsageResponse(BaseModel):
    """Response model for currency usage statistics."""

    currency: str
    count: int
    total_amount: float


class SplitTrendResponse(BaseModel):
    """Response model for split creation trends."""

    date: str
    count: int


# ============================================================================
# ENDPOINTS
# ============================================================================


@analytics_router.get(
    "/users/{user_id}/stats",
    response_model=UserStatsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user_stats(
    request: Request,
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> UserStatsResponse:
    """Get statistics for a specific user.

    Args:
        request: FastAPI request object
        user_id: User ID
        db: Database session

    Returns:
        UserStatsResponse with user statistics

    Raises:
        HTTPException: If user not found (404)
    """
    try:
        logger.info(f"Fetching stats for user: {user_id}")

        # Verify user exists
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found",
            )

        # Get total splits owned by user
        splits_result = await db.execute(
            select(func.count(Split.id)).where(Split.owner_id == user_id)
        )
        total_splits = splits_result.scalar() or 0

        # Get splits this month
        month_start = datetime.utcnow().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        this_month_result = await db.execute(
            select(func.count(Split.id)).where(
                Split.owner_id == user_id,
                Split.created_at >= month_start,
            )
        )
        splits_this_month = this_month_result.scalar() or 0

        # Get total amount from payments for user's splits
        # First get user's split IDs
        user_splits_result = await db.execute(
            select(Split.id).where(Split.owner_id == user_id)
        )
        user_split_ids = [row[0] for row in user_splits_result.all()]

        if user_split_ids:
            total_amount_result = await db.execute(
                select(func.sum(Payment.amount)).where(
                    Payment.split_id.in_(user_split_ids)
                )
            )
            total_amount = total_amount_result.scalar() or 0.0
        else:
            total_amount = 0.0

        avg_split_amount = (
            round(total_amount / total_splits, 2) if total_splits > 0 else 0.0
        )

        return UserStatsResponse(
            user_id=user_id,
            total_splits=total_splits,
            total_amount=total_amount,
            splits_this_month=splits_this_month,
            avg_split_amount=avg_split_amount,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@analytics_router.get(
    "/overall",
    response_model=OverallStatsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_overall_stats(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> OverallStatsResponse:
    """Get overall application statistics.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        OverallStatsResponse with application-wide statistics
    """
    try:
        logger.info("Fetching overall statistics")

        # Get total users
        users_result = await db.execute(select(func.count(User.id)))
        total_users = users_result.scalar() or 0

        # Get total splits
        splits_result = await db.execute(select(func.count(Split.id)))
        total_splits = splits_result.scalar() or 0

        # Get total payments
        payments_result = await db.execute(select(func.count(Payment.id)))
        total_payments = payments_result.scalar() or 0

        # Get total amount processed
        amount_result = await db.execute(select(func.sum(Payment.amount)))
        total_amount_processed = amount_result.scalar() or 0.0

        # Get active users this month (users who created splits)
        month_start = datetime.utcnow().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        active_users_result = await db.execute(
            select(func.count(func.distinct(Split.owner_id))).where(
                Split.created_at >= month_start
            )
        )
        active_users_this_month = active_users_result.scalar() or 0

        return OverallStatsResponse(
            total_users=total_users,
            total_splits=total_splits,
            total_payments=total_payments,
            total_amount_processed=total_amount_processed,
            active_users_this_month=active_users_this_month,
        )

    except Exception as e:
        logger.error(f"Error fetching overall stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@analytics_router.get(
    "/currencies",
    response_model=List[CurrencyUsageResponse],
    status_code=status.HTTP_200_OK,
)
async def get_currency_usage(
    request: Request,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
) -> List[CurrencyUsageResponse]:
    """Get currency usage statistics.

    Args:
        request: FastAPI request object
        days: Number of days to look back (default: 30)
        db: Database session

    Returns:
        List of CurrencyUsageResponse sorted by count
    """
    try:
        logger.info(f"Fetching currency usage for last {days} days")

        # Get date threshold
        date_threshold = datetime.utcnow() - timedelta(days=days)

        # Get currency usage from splits
        # Note: We're using split currency field
        result = await db.execute(
            select(Split.currency).where(Split.created_at >= date_threshold).distinct()
        )
        currencies = [row[0] for row in result.all()]

        usage_stats = []
        for currency in currencies:
            # Get count and total amount for this currency
            count_result = await db.execute(
                select(func.count(Split.id)).where(
                    Split.currency == currency,
                    Split.created_at >= date_threshold,
                )
            )
            count = count_result.scalar() or 0

            # Get total amount from payments for splits with this currency
            split_ids_result = await db.execute(
                select(Split.id).where(
                    Split.currency == currency,
                    Split.created_at >= date_threshold,
                )
            )
            split_ids = [row[0] for row in split_ids_result.all()]

            if split_ids:
                amount_result = await db.execute(
                    select(func.sum(Payment.amount)).where(
                        Payment.split_id.in_(split_ids)
                    )
                )
                total_amount = amount_result.scalar() or 0.0
            else:
                total_amount = 0.0

            usage_stats.append(
                CurrencyUsageResponse(
                    currency=currency,
                    count=count,
                    total_amount=total_amount,
                )
            )

        # Sort by count descending
        usage_stats.sort(key=lambda x: x.count, reverse=True)

        return usage_stats

    except Exception as e:
        logger.error(f"Error fetching currency usage: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@analytics_router.get(
    "/trends",
    response_model=List[SplitTrendResponse],
    status_code=status.HTTP_200_OK,
)
async def get_split_trends(
    request: Request,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
) -> List[SplitTrendResponse]:
    """Get split creation trends over time.

    Args:
        request: FastAPI request object
        days: Number of days to look back (default: 30)
        db: Database session

    Returns:
        List of SplitTrendResponse with daily counts
    """
    try:
        logger.info(f"Fetching split trends for last {days} days")

        trends = []
        for i in range(days):
            # Calculate date for this day
            date = datetime.utcnow() - timedelta(days=days - i - 1)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            # Get count of splits created on this day
            result = await db.execute(
                select(func.count(Split.id)).where(
                    Split.created_at >= day_start,
                    Split.created_at < day_end,
                )
            )
            count = result.scalar() or 0

            trends.append(
                SplitTrendResponse(
                    date=day_start.strftime("%Y-%m-%d"),
                    count=count,
                )
            )

        return trends

    except Exception as e:
        logger.error(f"Error fetching split trends: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
