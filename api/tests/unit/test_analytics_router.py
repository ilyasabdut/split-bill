"""Unit tests for analytics router."""

import uuid
from datetime import datetime, timedelta

from fastapi import status
from src.db.models import (
    Group,
    Payment,
    Split,
    User,
)


class TestAnalyticsRouter:
    """Test cases for analytics router endpoints."""

    async def test_get_user_stats_empty(self, async_client, auth_headers, test_user):
        """Test getting user stats with no activity."""
        response = await async_client.get(
            f"/analytics/users/{test_user.id}/stats", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["total_splits_created"] == 0
        assert data["total_groups_owned"] == 0
        assert data["total_groups_joined"] == 0
        assert data["total_payments_confirmed"] == 0
        assert data["total_amount_paid"] == 0.0
        assert data["preferred_currency"] == "USD"
        assert data["member_since"] is not None

    async def test_get_user_stats_with_activity(
        self,
        async_client,
        auth_headers,
        db_session,
        test_user,
        test_group,
        test_split,
        test_payment,
    ):
        """Test getting user stats with activity."""
        # Create additional activity
        # Add user to another group
        other_group = Group(name="Other Group", owner_id=test_user.id)
        db_session.add(other_group)

        # Create another split
        split2 = Split(
            group_id=test_group.id,
            owner_id=test_user.id,
            receipt_data={"total": 50.0},
            split_results={"Test User": 50.0},
            currency="EUR",
        )
        db_session.add(split2)

        # Create confirmed payment
        confirmed_payment = Payment(
            split_id=test_split.id,
            person_name="Test User",
            amount=38.0,
            currency="USD",
            confirmed_at=datetime.utcnow(),
        )
        db_session.add(confirmed_payment)

        await db_session.commit()

        response = await async_client.get(
            f"/analytics/users/{test_user.id}/stats", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["total_splits_created"] == 2
        assert data["total_groups_owned"] == 2  # test_group and other_group
        assert data["total_groups_joined"] == 1  # test_group_member
        assert data["total_payments_confirmed"] == 1
        assert data["total_amount_paid"] == 38.0
        assert data["preferred_currency"] == "USD"  # Most used currency

    async def test_get_user_stats_different_user(
        self, async_client, auth_headers, db_session
    ):
        """Test getting stats for different user (should be forbidden)."""
        # Create another user
        other_user = User(
            api_key=str(uuid.uuid4()),
            name="Other User",
            email="other@example.com",
        )
        db_session.add(other_user)
        await db_session.commit()

        response = await async_client.get(
            f"/analytics/users/{other_user.id}/stats", headers=auth_headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_user_stats_unauthorized(self, async_client, test_user):
        """Test getting user stats without authentication."""
        response = await async_client.get(f"/analytics/users/{test_user.id}/stats")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_user_stats_not_found(self, async_client, auth_headers):
        """Test getting stats for non-existent user."""
        non_existent_id = 99999

        response = await async_client.get(
            f"/analytics/users/{non_existent_id}/stats", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_overall_stats_empty(self, async_client, auth_headers):
        """Test getting overall stats with no data."""
        response = await async_client.get("/analytics/overall", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_users"] == 1  # test_user
        assert data["total_groups"] == 0
        assert data["total_splits"] == 0
        assert data["total_payments"] == 0
        assert data["total_amount_processed"] == 0.0
        assert data["average_split_amount"] == 0.0
        assert data["most_popular_currency"] == "USD"

    async def test_get_overall_stats_with_data(
        self,
        async_client,
        auth_headers,
        db_session,
        test_user,
        test_group,
        test_split,
        test_payment,
    ):
        """Test getting overall stats with data."""
        # Create additional users
        user2 = User(
            api_key=str(uuid.uuid4()), name="User 2", email="user2@example.com"
        )
        user3 = User(
            api_key=str(uuid.uuid4()), name="User 3", email="user3@example.com"
        )
        db_session.add_all([user2, user3])

        # Create additional groups
        group2 = Group(name="Group 2", owner_id=user2.id)
        group3 = Group(name="Group 3", owner_id=user3.id)
        db_session.add_all([group2, group3])

        # Create additional splits with different currencies
        split2 = Split(
            group_id=test_group.id,
            owner_id=test_user.id,
            receipt_data={"total": 100.0},
            split_results={"Test User": 100.0},
            currency="EUR",
        )
        split3 = Split(
            group_id=group2.id,
            owner_id=user2.id,
            receipt_data={"total": 75.0},
            split_results={"User 2": 75.0},
            currency="GBP",
        )
        db_session.add_all([split2, split3])

        # Create additional payments
        payment2 = Payment(
            split_id=split2.id,
            person_name="Test User",
            amount=100.0,
            currency="EUR",
            confirmed_at=datetime.utcnow(),
        )
        payment3 = Payment(
            split_id=split3.id,
            person_name="User 2",
            amount=75.0,
            currency="GBP",
        )
        db_session.add_all([payment2, payment3])

        await db_session.commit()

        response = await async_client.get("/analytics/overall", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_users"] == 4
        assert data["total_groups"] == 4
        assert data["total_splits"] == 3
        assert data["total_payments"] == 3
        assert data["total_amount_processed"] == 213.0  # 38 + 100 + 75
        assert data["average_split_amount"] == 71.0  # (38 + 100 + 75) / 3
        assert data["most_popular_currency"] == "USD"  # Most frequent

    async def test_get_overall_stats_unauthorized(self, async_client):
        """Test getting overall stats without authentication."""
        response = await async_client.get("/analytics/overall")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_currency_usage_empty(self, async_client, auth_headers):
        """Test getting currency usage with no splits."""
        response = await async_client.get("/analytics/currencies", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["currencies"] == []
        assert data["total_splits"] == 0

    async def test_get_currency_usage_with_data(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test getting currency usage with splits."""
        # Create groups and splits with different currencies
        group1 = Group(name="Group 1", owner_id=test_user.id)
        group2 = Group(name="Group 2", owner_id=test_user.id)
        db_session.add_all([group1, group2])
        await db_session.flush()

        # USD splits
        for i in range(3):
            split = Split(
                group_id=group1.id,
                owner_id=test_user.id,
                receipt_data={"total": 100.0 * (i + 1)},
                split_results={"Test User": 100.0 * (i + 1)},
                currency="USD",
            )
            db_session.add(split)

        # EUR splits
        for i in range(2):
            split = Split(
                group_id=group2.id,
                owner_id=test_user.id,
                receipt_data={"total": 50.0 * (i + 1)},
                split_results={"Test User": 50.0 * (i + 1)},
                currency="EUR",
            )
            db_session.add(split)

        # GBP split
        split_gbp = Split(
            group_id=group1.id,
            owner_id=test_user.id,
            receipt_data={"total": 75.0},
            split_results={"Test User": 75.0},
            currency="GBP",
        )
        db_session.add(split_gbp)

        await db_session.commit()

        response = await async_client.get("/analytics/currencies", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_splits"] == 6
        assert len(data["currencies"]) == 3

        # Check currency breakdown
        currencies = {c["currency"]: c for c in data["currencies"]}
        assert currencies["USD"]["count"] == 3
        assert currencies["USD"]["total_amount"] == 600.0  # 100 + 200 + 300
        assert currencies["EUR"]["count"] == 2
        assert currencies["EUR"]["total_amount"] == 150.0  # 50 + 100
        assert currencies["GBP"]["count"] == 1
        assert currencies["GBP"]["total_amount"] == 75.0

    async def test_get_currency_usage_unauthorized(self, async_client):
        """Test getting currency usage without authentication."""
        response = await async_client.get("/analytics/currencies")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_split_trends_empty(self, async_client, auth_headers):
        """Test getting split trends with no data."""
        response = await async_client.get("/analytics/trends", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["trends"] == []
        assert data["total_splits"] == 0
        assert data["date_range"] == {}

    async def test_get_split_trends_with_data(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test getting split trends with data."""
        # Create splits over different dates
        today = datetime.utcnow()

        # Today
        split1 = Split(
            group_id=test_user.groups[0].id,
            owner_id=test_user.id,
            receipt_data={"total": 100.0},
            split_results={"Test User": 100.0},
            currency="USD",
            created_at=today,
        )

        # Yesterday
        split2 = Split(
            group_id=test_user.groups[0].id,
            owner_id=test_user.id,
            receipt_data={"total": 150.0},
            split_results={"Test User": 150.0},
            currency="USD",
            created_at=today - timedelta(days=1),
        )

        # 2 days ago
        split3 = Split(
            group_id=test_user.groups[0].id,
            owner_id=test_user.id,
            receipt_data={"total": 200.0},
            split_results={"Test User": 200.0},
            currency="USD",
            created_at=today - timedelta(days=2),
        )

        db_session.add_all([split1, split2, split3])
        await db_session.commit()

        response = await async_client.get("/analytics/trends", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_splits"] == 4  # Including test_split from fixture
        assert len(data["trends"]) >= 3  # At least 3 different dates

        # Check that trends are grouped by date
        dates = [t["date"] for t in data["trends"]]
        assert len(set(dates)) == len(dates)  # All dates should be unique

    async def test_get_split_trends_with_date_range(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test getting split trends with date range filter."""
        # Create splits with specific dates
        today = datetime.utcnow()

        # Old split (10 days ago)
        old_split = Split(
            group_id=test_user.groups[0].id,
            owner_id=test_user.id,
            receipt_data={"total": 100.0},
            split_results={"Test User": 100.0},
            currency="USD",
            created_at=today - timedelta(days=10),
        )

        # Recent splits (within last 7 days)
        for i in range(3):
            split = Split(
                group_id=test_user.groups[0].id,
                owner_id=test_user.id,
                receipt_data={"total": 50.0 * (i + 1)},
                split_results={"Test User": 50.0 * (i + 1)},
                currency="USD",
                created_at=today - timedelta(days=i),
            )
            db_session.add(split)

        db_session.add(old_split)
        await db_session.commit()

        # Get trends for last 7 days
        start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

        response = await async_client.get(
            f"/analytics/trends?start_date={start_date}&end_date={end_date}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should only include splits from last 7 days (3 recent + test_split)
        total_recent = sum(t["count"] for t in data["trends"])
        assert total_recent == 4

    async def test_get_split_trends_invalid_date_format(
        self, async_client, auth_headers
    ):
        """Test getting split trends with invalid date format."""
        response = await async_client.get(
            "/analytics/trends?start_date=invalid", headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_split_trends_future_date(self, async_client, auth_headers):
        """Test getting split trends with future date."""
        future_date = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")

        response = await async_client.get(
            f"/analytics/trends?end_date={future_date}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_get_split_trends_unauthorized(self, async_client):
        """Test getting split trends without authentication."""
        response = await async_client.get("/analytics/trends")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
