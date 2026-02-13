"""Unit tests for currency service."""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest_asyncio
from sqlalchemy import select
from src.db.models import CurrencyRate
from src.services.currency_service import CurrencyService


class TestCurrencyService:
    """Test cases for CurrencyService."""

    @pytest_asyncio.fixture
    async def currency_service(self):
        """Create a currency service instance."""
        service = CurrencyService()
        yield service
        await service.close()

    @pytest_asyncio.fixture
    def mock_rate_response(self):
        """Mock currency API response."""
        return {
            "result": "success",
            "base_code": "USD",
            "rates": {
                "EUR": 0.85,
                "GBP": 0.73,
                "JPY": 110.0,
                "CAD": 1.25,
                "AUD": 1.35,
            },
        }

    async def test_get_rate_same_currency(self, currency_service):
        """Test getting rate for same currency."""
        rate = await currency_service.get_rate("USD", "USD")
        assert rate == 1.0

    async def test_get_rate_from_cache(
        self, db_session, currency_service, test_currency_rate
    ):
        """Test getting rate from cache."""
        rate = await currency_service.get_rate("USD", "EUR")
        assert rate == 0.85

    async def test_get_rate_from_api(self, currency_service, mock_rate_response):
        """Test getting rate from external API."""
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_rate_response
        mock_response.raise_for_status = MagicMock()

        with patch.object(currency_service.client, "get", return_value=mock_response):
            rate = await currency_service.get_rate("USD", "GBP")
            assert rate == 0.73

    async def test_get_rate_api_failure(self, currency_service):
        """Test handling API failure."""
        # Mock API failure
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.raise_for_status = MagicMock(
            side_effect=Exception("500 Server Error")
        )

        with patch.object(currency_service.client, "get", return_value=mock_response):
            rate = await currency_service.get_rate("USD", "EUR")
            assert rate is None

    async def test_get_rate_missing_target_currency(self, currency_service):
        """Test handling when target currency not in API response."""
        # Mock response without EUR
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": "success",
            "base_code": "USD",
            "rates": {
                "GBP": 0.73,
                "JPY": 110.0,
            },
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(currency_service.client, "get", return_value=mock_response):
            rate = await currency_service.get_rate("USD", "EUR")
            assert rate is None

    async def test_cache_rate_expiration(
        self, db_session, currency_service, mock_rate_response
    ):
        """Test that cached rates expire after 24 hours."""
        # Create an old cached rate
        old_rate = CurrencyRate(
            from_currency="USD",
            to_currency="EUR",
            rate=0.80,
            updated_at=datetime.utcnow() - timedelta(hours=25),
        )
        db_session.add(old_rate)
        await db_session.commit()

        # Mock API response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_rate_response
        mock_response.raise_for_status = MagicMock()

        with patch.object(currency_service.client, "get", return_value=mock_response):
            # Should fetch new rate because old one is expired
            rate = await currency_service.get_rate("USD", "EUR")
            assert rate == 0.85  # New rate from API

    async def test_convert_currency(
        self, db_session, currency_service, test_currency_rate
    ):
        """Test currency conversion."""
        amount = 100.0
        converted = await currency_service.convert(amount, "USD", "EUR")
        assert converted == 85.0  # 100 * 0.85

    async def test_convert_same_currency(self, currency_service):
        """Test converting to same currency."""
        amount = 100.0
        converted = await currency_service.convert(amount, "USD", "USD")
        assert converted == 100.0

    async def test_convert_zero_amount(
        self, db_session, currency_service, test_currency_rate
    ):
        """Test converting zero amount."""
        converted = await currency_service.convert(0.0, "USD", "EUR")
        assert converted == 0.0

    async def test_convert_negative_amount(
        self, db_session, currency_service, test_currency_rate
    ):
        """Test converting negative amount."""
        converted = await currency_service.convert(-50.0, "USD", "EUR")
        assert converted == -42.5  # -50 * 0.85

    async def test_convert_rate_not_found(self, currency_service):
        """Test conversion when rate not found."""
        # Mock API failure
        mock_response = AsyncMock()
        mock_response.raise_for = MagicMock(side_effect=Exception("Network error"))

        with patch.object(currency_service.client, "get", return_value=mock_response):
            converted = await currency_service.convert(100.0, "USD", "XXX")
            assert converted is None

    async def test_cache_rate_function(self, db_session, currency_service):
        """Test caching a rate."""
        await currency_service._cache_rate("USD", "GBP", 0.73)

        # Verify rate was cached
        result = await db_session.execute(
            select(CurrencyRate).where(
                CurrencyRate.from_currency == "USD", CurrencyRate.to_currency == "GBP"
            )
        )
        cached_rate = result.scalar_one()

        assert cached_rate.rate == 0.73
        assert cached_rate.updated_at is not None

    async def test_cache_rate_update(
        self, db_session, currency_service, test_currency_rate
    ):
        """Test updating an existing cached rate."""
        # Update the existing rate
        new_rate = 0.90
        await currency_service._cache_rate("USD", "EUR", new_rate)

        # Verify rate was updated
        result = await db_session.execute(
            select(CurrencyRate).where(
                CurrencyRate.from_currency == "USD", CurrencyRate.to_currency == "EUR"
            )
        )
        updated_rate = result.scalar_one()

        assert updated_rate.rate == 0.90
        assert updated_rate.id == test_currency_rate.id  # Same record

    async def test_get_cached_rate_not_found(self, currency_service):
        """Test getting non-existent cached rate."""
        rate = await currency_service._get_cached_rate("XXX", "YYY")
        assert rate is None

    async def test_get_cached_rate_expired(self, db_session, currency_service):
        """Test getting expired cached rate."""
        # Create an expired rate
        expired_rate = CurrencyRate(
            from_currency="USD",
            to_currency="EUR",
            rate=0.80,
            updated_at=datetime.utcnow() - timedelta(hours=25),
        )
        db_session.add(expired_rate)
        await db_session.commit()

        # Should return None for expired rate
        rate = await currency_service._get_cached_rate("USD", "EUR")
        assert rate is None

    async def test_get_cached_rate_valid(self, db_session, currency_service):
        """Test getting valid cached rate."""
        # Create a valid rate (recent)
        valid_rate = CurrencyRate(
            from_currency="USD",
            to_currency="GBP",
            rate=0.73,
            updated_at=datetime.utcnow() - timedelta(hours=1),
        )
        db_session.add(valid_rate)
        await db_session.commit()

        # Should return rate
        rate = await currency_service._get_cached_rate("USD", "GBP")
        assert rate == 0.73

    async def test_rate_caching_concurrent(
        self, db_session, currency_service, mock_rate_response
    ):
        """Test concurrent rate fetching doesn't create duplicates."""
        # Mock API response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_rate_response
        mock_response.raise_for_status = MagicMock()

        with patch.object(currency_service.client, "get", return_value=mock_response):
            # Fetch same rate concurrently
            tasks = [
                currency_service.get_rate("USD", "CAD"),
                currency_service.get_rate("USD", "CAD"),
                currency_service.get_rate("USD", "CAD"),
            ]
            rates = await asyncio.gather(*tasks)

            # All should return same rate
            assert all(rate == 1.25 for rate in rates)

            # Should only have one cached rate
            result = await db_session.execute(
                select(CurrencyRate).where(
                    CurrencyRate.from_currency == "USD",
                    CurrencyRate.to_currency == "CAD",
                )
            )
            cached_rates = result.scalars().all()
            assert len(cached_rates) == 1

    async def test_rate_precision(self, currency_service):
        """Test rate precision handling."""
        # Mock response with high precision rate
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": "success",
            "base_code": "USD",
            "rates": {
                "BTC": 0.000025123456789,  # High precision
            },
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(currency_service.client, "get", return_value=mock_response):
            rate = await currency_service.get_rate("USD", "BTC")
            assert rate == 0.000025123456789

    async def test_multiple_currency_fetch(self, currency_service, mock_rate_response):
        """Test fetching multiple currencies in one call."""
        # Mock API response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_rate_response
        mock_response.raise_for_status = MagicMock()

        with patch.object(currency_service.client, "get", return_value=mock_response):
            # Fetch multiple rates
            rates = await asyncio.gather(
                currency_service.get_rate("USD", "EUR"),
                currency_service.get_rate("USD", "GBP"),
                currency_service.get_rate("USD", "JPY"),
            )

            assert rates[0] == 0.85
            assert rates[1] == 0.73
            assert rates[2] == 110.0

    async def test_currency_code_case_insensitive(self, db_session, currency_service):
        """Test that currency codes are case-insensitive."""
        # Create cached rate with uppercase
        await currency_service._cache_rate("USD", "EUR", 0.85)

        # Fetch with lowercase
        rate = await currency_service.get_rate("usd", "eur")
        assert rate == 0.85

    async def test_close_client(self, currency_service):
        """Test closing HTTP client."""
        # Should not raise an exception
        await currency_service.close()

    async def test_fetch_rate_from_api_success(self, currency_service):
        """Test successful rate fetch from API."""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": "success",
            "base_code": "USD",
            "rates": {
                "EUR": 0.85,
            },
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(currency_service.client, "get", return_value=mock_response):
            rate = await currency_service._fetch_rate_from_api("USD", "EUR")
            assert rate == 0.85

    async def test_fetch_rate_from_api_no_rates_key(self):
        """Test API response without rates key."""
        service = CurrencyService()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": "success",
            "base_code": "USD",
            # Missing "rates" key
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(service.client, "get", return_value=mock_response):
            rate = await service._fetch_rate_from_api("USD", "EUR")
            assert rate is None
        await service.close()

    async def test_fetch_rate_from_api_empty_rates(self):
        """Test API response with empty rates."""
        service = CurrencyService()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": "success",
            "base_code": "USD",
            "rates": {},
        }
        mock_response.raise_for_status = MagicMock()

        with patch.object(service.client, "get", return_value=mock_response):
            rate = await service._fetch_rate_from_api("USD", "EUR")
            assert rate is None
        await service.close()

    async def test_fetch_rate_from_api_http_error(self):
        """Test handling HTTP status error."""
        service = CurrencyService()
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.raise_for_status = MagicMock(
            httpx.HTTPStatusError(
                "Not Found", request=MagicMock(), response=MagicMock()
            )
        )

        with patch.object(service.client, "get", return_value=mock_response):
            rate = await service._fetch_rate_from_api("USD", "EUR")
            assert rate is None
        await service.close()

    async def test_fetch_rate_from_api_network_error(self):
        """Test handling network error."""
        service = CurrencyService()
        mock_get = AsyncMock(side_effect=Exception("Network error"))

        with patch.object(service.client, "get", mock_get):
            rate = await service._fetch_rate_from_api("USD", "EUR")
            assert rate is None
        await service.close()

    async def test_convert_rounding(
        self, db_session, currency_service, test_currency_rate
    ):
        """Test that conversion rounds to 2 decimal places."""
        # 100 * 0.85 = 85.0 (no rounding needed)
        result1 = await currency_service.convert(100.0, "USD", "EUR")
        assert result1 == 85.0

        # 33.33 * 0.85 = 28.3305 -> 28.33
        result2 = await currency_service.convert(33.33, "USD", "EUR")
        assert result2 == 28.33

    async def test_get_rate_exception_handling(self, currency_service):
        """Test exception handling in get_rate."""
        # Mock get to raise exception
        mock_get = AsyncMock(side_effect=Exception("Unexpected error"))

        with patch.object(currency_service.client, "get", mock_get):
            rate = await currency_service.get_rate("USD", "EUR")
            assert rate is None
