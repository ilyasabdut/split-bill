"""Unit tests for payments router."""

import uuid
from datetime import datetime

from fastapi import status
from sqlalchemy import select


class TestPaymentsRouter:
    """Test cases for payments router endpoints."""

    async def test_create_payment_success(self, async_client, auth_headers, test_split):
        """Test creating a payment successfully."""
        payment_data = {
            "split_id": test_split.id,
            "person_name": "John Doe",
            "amount": 25.0,
            "currency": "USD",
        }

        response = await async_client.post(
            "/payments/", json=payment_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["split_id"] == test_split.id
        assert data["person_name"] == "John Doe"
        assert data["amount"] == 25.0
        assert data["currency"] == "USD"
        assert "id" in data
        assert "created_at" in data

    async def test_create_payment_unauthorized(self, async_client, test_split):
        """Test creating payment without authentication."""
        payment_data = {
            "split_id": test_split.id,
            "person_name": "John Doe",
            "amount": 25.0,
            "currency": "USD",
        }

        response = await async_client.post("/payments/", json=payment_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_payment_invalid_api_key(self, async_client, test_split):
        """Test creating payment with invalid API key."""
        payment_data = {
            "split_id": test_split.id,
            "person_name": "John Doe",
            "amount": 25.0,
            "currency": "USD",
        }
        headers = {"X-API-Key": "invalid-key"}

        response = await async_client.post(
            "/payments/", json=payment_data, headers=headers
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_payment_missing_fields(self, async_client, auth_headers):
        """Test creating payment with missing required fields."""
        # Missing split_id
        payment_data = {
            "person_name": "John Doe",
            "amount": 25.0,
            "currency": "USD",
        }

        response = await async_client.post(
            "/payments/", json=payment_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Missing person_name
        payment_data = {
            "split_id": 1,
            "amount": 25.0,
            "currency": "USD",
        }

        response = await async_client.post(
            "/payments/", json=payment_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Missing amount
        payment_data = {
            "split_id": 1,
            "person_name": "John Doe",
            "currency": "USD",
        }

        response = await async_client.post(
            "/payments/", json=payment_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_payment_invalid_amount(
        self, async_client, auth_headers, test_split
    ):
        """Test creating payment with invalid amount."""
        # Negative amount
        payment_data = {
            "split_id": test_split.id,
            "person_name": "John Doe",
            "amount": -25.0,
            "currency": "USD",
        }

        response = await async_client.post(
            "/payments/", json=payment_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Zero amount
        payment_data["amount"] = 0.0
        response = await async_client.post(
            "/payments/", json=payment_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_payment_invalid_currency(
        self, async_client, auth_headers, test_split
    ):
        """Test creating payment with invalid currency."""
        payment_data = {
            "split_id": test_split.id,
            "person_name": "John Doe",
            "amount": 25.0,
            "currency": "INVALID",
        }

        response = await async_client.post(
            "/payments/", json=payment_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_payment_nonexistent_split(self, async_client, auth_headers):
        """Test creating payment for non-existent split."""
        payment_data = {
            "split_id": 99999,
            "person_name": "John Doe",
            "amount": 25.0,
            "currency": "USD",
        }

        response = await async_client.post(
            "/payments/", json=payment_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_payment_not_group_member(
        self, async_client, auth_headers, db_session, test_user
    ):
        """Test creating payment when user is not in the split's group."""
        # Create another user and group
        other_user = User(
            api_key=str(uuid.uuid4()),
            name="Other User",
            email="other@example.com",
        )
        db_session.add(other_user)
        await db_session.commit()

        from src.db.models import Group

        other_group = Group(name="Other Group", owner_id=other_user.id)
        db_session.add(other_group)
        await db_session.commit()

        other_split = Split(
            group_id=other_group.id,
            owner_id=other_user.id,
            receipt_data={"total": 100.0},
            split_results={"Other": 100.0},
            currency="USD",
        )
        db_session.add(other_split)
        await db_session.commit()

        payment_data = {
            "split_id": other_split.id,
            "person_name": "John Doe",
            "amount": 25.0,
            "currency": "USD",
        }

        response = await async_client.post(
            "/payments/", json=payment_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_payment_success(self, async_client, auth_headers, test_payment):
        """Test getting a payment successfully."""
        response = await async_client.get(
            f"/payments/{test_payment.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_payment.id
        assert data["split_id"] == test_payment.split_id
        assert data["person_name"] == test_payment.person_name
        assert data["amount"] == test_payment.amount
        assert data["currency"] == test_payment.currency
        assert data["status"] == test_payment.status.value

    async def test_get_payment_not_found(self, async_client, auth_headers):
        """Test getting non-existent payment."""
        non_existent_id = 99999

        response = await async_client.get(
            f"/payments/{non_existent_id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_payment_unauthorized(self, async_client, test_payment):
        """Test getting payment without authentication."""
        response = await async_client.get(f"/payments/{test_payment.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_payment_not_owner(self, async_client, auth_headers, db_session):
        """Test getting payment from split user doesn't have access to."""
        # Create another user, group, split, and payment
        other_user = User(
            api_key=str(uuid.uuid4()),
            name="Other User",
            email="other@example.com",
        )
        db_session.add(other_user)
        await db_session.commit()

        from src.db.models import Group

        other_group = Group(name="Other Group", owner_id=other_user.id)
        db_session.add(other_group)
        await db_session.commit()

        other_split = Split(
            group_id=other_group.id,
            owner_id=other_user.id,
            receipt_data={"total": 100.0},
            split_results={"Other": 100.0},
            currency="USD",
        )
        db_session.add(other_split)
        await db_session.commit()

        other_payment = Payment(
            split_id=other_split.id,
            person_name="Other Person",
            amount=50.0,
            currency="USD",
        )
        db_session.add(other_payment)
        await db_session.commit()

        response = await async_client.get(
            f"/payments/{other_payment.id}", headers=auth_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_list_payments_empty(self, async_client, auth_headers):
        """Test listing payments when user has none."""
        response = await async_client.get("/payments/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["payments"] == []
        assert data["total"] == 0

    async def test_list_payments_with_data(
        self, async_client, auth_headers, db_session, test_user, test_split
    ):
        """Test listing payments with existing payments."""
        # Create multiple payments
        payments = []
        for i in range(3):
            payment = Payment(
                split_id=test_split.id,
                person_name=f"Person {i+1}",
                amount=10.0 * (i + 1),
                currency="USD",
            )
            db_session.add(payment)
            payments.append(payment)
        await db_session.commit()

        response = await async_client.get("/payments/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["payments"]) == 4  # Including test_payment from fixture
        assert data["total"] == 4
        assert all("id" in p and "person_name" in p for p in data["payments"])

    async def test_list_payments_pagination(
        self, async_client, auth_headers, db_session, test_user, test_split
    ):
        """Test payment listing with pagination."""
        # Create multiple payments
        for i in range(5):
            payment = Payment(
                split_id=test_split.id,
                person_name=f"Person {i+1}",
                amount=10.0,
                currency="USD",
            )
            db_session.add(payment)
        await db_session.commit()

        # Get first page
        response = await async_client.get(
            "/payments/?skip=0&limit=2", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["payments"]) == 2

        # Get second page
        response = await async_client.get(
            "/payments/?skip=2&limit=2", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["payments"]) == 2

    async def test_list_payments_filter_by_status(
        self, async_client, auth_headers, db_session, test_user, test_split
    ):
        """Test filtering payments by status."""
        # Create payments with different statuses
        pending_payment = Payment(
            split_id=test_split.id,
            person_name="Pending Person",
            amount=10.0,
            currency="USD",
        )
        confirmed_payment = Payment(
            split_id=test_split.id,
            person_name="Confirmed Person",
            amount=20.0,
            currency="USD",
        )
        db_session.add_all([pending_payment, confirmed_payment])
        await db_session.commit()

        # Filter by pending status
        response = await async_client.get(
            "/payments/?status=pending", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(p["status"] == "pending" for p in data["payments"])

        # Filter by confirmed status
        response = await async_client.get(
            "/payments/?status=confirmed", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(p["status"] == "confirmed" for p in data["payments"])

    async def test_update_payment_status_success(
        self, async_client, auth_headers, test_payment
    ):
        """Test updating payment status successfully."""
        update_data = {
            "status": "confirmed",
        }

        response = await async_client.put(
            f"/payments/{test_payment.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_payment.id
        assert data["status"] == "confirmed"
        assert data["confirmed_at"] is not None

    async def test_update_payment_status_invalid_transition(
        self, async_client, auth_headers, db_session, test_split
    ):
        """Test invalid payment status transition."""
        # Create a confirmed payment
        confirmed_payment = Payment(
            split_id=test_split.id,
            person_name="Confirmed Person",
            amount=30.0,
            currency="USD",
            confirmed_at=datetime.utcnow(),
        )
        db_session.add(confirmed_payment)
        await db_session.commit()

        # Try to change back to pending
        update_data = {
            "status": "pending",
        }

        response = await async_client.put(
            f"/payments/{confirmed_payment.id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_payment_amount(
        self, async_client, auth_headers, test_payment
    ):
        """Test updating payment amount."""
        update_data = {
            "amount": 50.0,
        }

        response = await async_client.put(
            f"/payments/{test_payment.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["amount"] == 50.0

    async def test_update_payment_not_found(self, async_client, auth_headers):
        """Test updating non-existent payment."""
        non_existent_id = 99999
        update_data = {
            "status": "confirmed",
        }

        response = await async_client.put(
            f"/payments/{non_existent_id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_payment_not_owner(
        self, async_client, auth_headers, db_session
    ):
        """Test updating payment from split user doesn't have access to."""
        # Create another user, group, split, and payment
        other_user = User(
            api_key=str(uuid.uuid4()),
            name="Other User",
            email="other@example.com",
        )
        db_session.add(other_user)
        await db_session.commit()

        from src.db.models import Group

        other_group = Group(name="Other Group", owner_id=other_user.id)
        db_session.add(other_group)
        await db_session.commit()

        other_split = Split(
            group_id=other_group.id,
            owner_id=other_user.id,
            receipt_data={"total": 100.0},
            split_results={"Other": 100.0},
            currency="USD",
        )
        db_session.add(other_split)
        await db_session.commit()

        other_payment = Payment(
            split_id=other_split.id,
            person_name="Other Person",
            amount=50.0,
            currency="USD",
        )
        db_session.add(other_payment)
        await db_session.commit()

        update_data = {
            "status": "confirmed",
        }

        response = await async_client.put(
            f"/payments/{other_payment.id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_payment_success(
        self, async_client, auth_headers, test_payment, db_session
    ):
        """Test deleting a payment successfully."""
        response = await async_client.delete(
            f"/payments/{test_payment.id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify payment was deleted
        result = await db_session.execute(
            select(Payment).where(Payment.id == test_payment.id)
        )
        deleted_payment = result.scalar_one_or_none()
        assert deleted_payment is None

    async def test_delete_payment_not_found(self, async_client, auth_headers):
        """Test deleting non-existent payment."""
        non_existent_id = 99999

        response = await async_client.delete(
            f"/payments/{non_existent_id}", headers=auth_headers
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_payment_not_owner(
        self, async_client, auth_headers, db_session
    ):
        """Test deleting payment from split user doesn't have access to."""
        # Create another user, group, split, and payment
        other_user = User(
            api_key=str(uuid.uuid4()),
            name="Other User",
            email="other@example.com",
        )
        db_session.add(other_user)
        await db_session.commit()

        from src.db.models import Group

        other_group = Group(name="Other Group", owner_id=other_user.id)
        db_session.add(other_group)
        await db_session.commit()

        other_split = Split(
            group_id=other_group.id,
            owner_id=other_user.id,
            receipt_data={"total": 100.0},
            split_results={"Other": 100.0},
            currency="USD",
        )
        db_session.add(other_split)
        await db_session.commit()

        other_payment = Payment(
            split_id=other_split.id,
            person_name="Other Person",
            amount=50.0,
            currency="USD",
        )
        db_session.add(other_payment)
        await db_session.commit()

        response = await async_client.delete(
            f"/payments/{other_payment.id}", headers=auth_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_split_payment_summary_success(
        self, async_client, auth_headers, test_split, db_session
    ):
        """Test getting payment summary for a split."""
        # Create multiple payments for the split
        payments = [
            Payment(
                split_id=test_split.id,
                person_name="Alice",
                amount=30.0,
                currency="USD",
            ),
            Payment(
                split_id=test_split.id,
                person_name="Bob",
                amount=20.0,
                currency="USD",
            ),
            Payment(
                split_id=test_split.id,
                person_name="Charlie",
                amount=50.0,
                currency="USD",
            ),
        ]
        db_session.add_all(payments)
        await db_session.commit()

        response = await async_client.get(
            f"/payments/split/{test_split.id}/summary", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["split_id"] == test_split.id
        assert data["total_payments"] == 4  # Including test_payment from fixture
        assert data["total_confirmed"] == 2
        assert data["total_pending"] == 1
        assert data["total_amount"] == 138.0  # 38 + 30 + 20 + 50
        assert data["confirmed_amount"] == 118.0  # 38 + 30 + 50
        assert data["pending_amount"] == 20.0

    async def test_get_split_payment_summary_empty(
        self, async_client, auth_headers, test_split, db_session
    ):
        """Test getting payment summary for split with no payments."""
        # Delete all payments for the split
        await db_session.execute(
            select(Payment).where(Payment.split_id == test_split.id)
        )
        payments = await db_session.execute(
            select(Payment).where(Payment.split_id == test_split.id)
        )
        for payment in payments.scalars().all():
            await db_session.delete(payment)
        await db_session.commit()

        response = await async_client.get(
            f"/payments/split/{test_split.id}/summary", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["split_id"] == test_split.id
        assert data["total_payments"] == 0
        assert data["total_confirmed"] == 0
        assert data["total_pending"] == 0
        assert data["total_amount"] == 0.0
        assert data["confirmed_amount"] == 0.0
        assert data["pending_amount"] == 0.0

    async def test_get_split_payment_summary_not_member(
        self, async_client, auth_headers, db_session
    ):
        """Test getting payment summary for split user doesn't have access to."""
        # Create another user, group, and split
        other_user = User(
            api_key=str(uuid.uuid4()),
            name="Other User",
            email="other@example.com",
        )
        db_session.add(other_user)
        await db_session.commit()

        from src.db.models import Group

        other_group = Group(name="Other Group", owner_id=other_user.id)
        db_session.add(other_group)
        await db_session.commit()

        other_split = Split(
            group_id=other_group.id,
            owner_id=other_user.id,
            receipt_data={"total": 100.0},
            split_results={"Other": 100.0},
            currency="USD",
        )
        db_session.add(other_split)
        await db_session.commit()

        response = await async_client.get(
            f"/payments/split/{other_split.id}/summary", headers=auth_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_split_payment_summary_not_found(
        self, async_client, auth_headers
    ):
        """Test getting payment summary for non-existent split."""
        non_existent_id = 99999

        response = await async_client.get(
            f"/payments/split/{non_existent_id}/summary", headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
