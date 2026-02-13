"""Currency exchange rate service.

This module handles currency conversion and rate caching.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx
from src.db.database import async_session_maker
from src.db.models import CurrencyRate

logger = logging.getLogger(__name__)


# Free exchange rate API
EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest"


class CurrencyService:
    """Service for currency exchange operations."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def get_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Get exchange rate between two currencies.

        Args:
            from_currency: Source currency code (e.g., "USD", "IDR")
            to_currency: Target currency code (e.g., "USD", "IDR")

        Returns:
            Exchange rate or None if unavailable
        """
        if from_currency.upper() == to_currency.upper():
            return 1.0

        # Check database for cached rate (valid for 24 hours)
        cached_rate = await self._get_cached_rate(from_currency, to_currency)
        if cached_rate:
            return cached_rate

        # Fetch from API
        try:
            rate = await self._fetch_rate_from_api(from_currency, to_currency)
            if rate:
                # Cache the rate
                await self._cache_rate(from_currency, to_currency, rate)
            return rate
        except Exception as e:
            logger.error(f"Failed to fetch exchange rate: {e}")
            return None

    async def convert(
        self, amount: float, from_currency: str, to_currency: str
    ) -> Optional[float]:
        """Convert amount between currencies.

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Converted amount or None if conversion failed
        """
        rate = await self.get_rate(from_currency, to_currency)
        if rate is None:
            return None
        return round(amount * rate, 2)

    async def _get_cached_rate(
        self, from_currency: str, to_currency: str
    ) -> Optional[float]:
        """Get cached exchange rate from database."""
        async with async_session_maker() as session:
            from datetime import datetime

            from sqlalchemy import select

            stmt = select(CurrencyRate).where(
                CurrencyRate.from_currency == from_currency.upper(),
                CurrencyRate.to_currency == to_currency.upper(),
            )
            result = await session.execute(stmt)
            rate_record = result.scalar_one_or_none()

            if rate_record:
                # Check if cache is still valid (24 hours)
                if datetime.utcnow() - rate_record.updated_at < timedelta(hours=24):
                    return rate_record.rate

        return None

    async def _cache_rate(
        self, from_currency: str, to_currency: str, rate: float
    ) -> None:
        """Cache exchange rate in database."""
        async with async_session_maker() as session:
            from sqlalchemy import select

            stmt = select(CurrencyRate).where(
                CurrencyRate.from_currency == from_currency.upper(),
                CurrencyRate.to_currency == to_currency.upper(),
            )
            result = await session.execute(stmt)
            rate_record = result.scalar_one_or_none()

            if rate_record:
                # Update existing record
                rate_record.rate = rate
                rate_record.updated_at = datetime.utcnow()
            else:
                # Create new record
                rate_record = CurrencyRate(
                    from_currency=from_currency.upper(),
                    to_currency=to_currency.upper(),
                    rate=rate,
                )
                session.add(rate_record)

            await session.commit()

    async def _fetch_rate_from_api(
        self, from_currency: str, to_currency: str
    ) -> Optional[float]:
        """Fetch exchange rate from external API."""
        try:
            response = await self.client.get(
                f"{EXCHANGE_RATE_API}/{from_currency.upper()}"
            )
            response.raise_for_status()
            data = response.json()

            if "rates" in data and to_currency.upper() in data["rates"]:
                return float(data["rates"][to_currency.upper()])

            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Exchange rate API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching exchange rate: {e}")
            return None


# Global service instance
currency_service = CurrencyService()
