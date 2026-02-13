"""Unit tests for database models."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import (
    CurrencyRate,
    Group,
    GroupMember,
    Payment,
    Split,
    Template,
    User,
)


class TestUserModel:
    """Test cases for User model."""

    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a user."""
        user_data = {
            "api_key": str(uuid.uuid4()),
            "name": "John Doe",
            "email": "john@example.com",
        }
        user = User(**user_data)
        db_session.add(user)
        await db_session.commit()

        # Verify user was created
        result = await db_session.execute(
            select(User).where(User.email == "john@example.com")
        )
        saved_user = result.scalar_one()

        assert saved_user.name == "John Doe"
        assert saved_user.email == "john@example.com"
        assert saved_user.api_key == user_data["api_key"]
        assert saved_user.created_at is not None
        assert isinstance(saved_user.created_at, datetime)

    async def test_user_api_key_unique(self, db_session: AsyncSession, test_user: User):
        """Test that API key must be unique."""
        # Try to create another user with the same API key
        user2 = User(
            api_key=test_user.api_key,
            name="Jane Doe",
            email="jane@example.com",
        )
        db_session.add(user2)

        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            await db_session.commit()

    async def test_user_email_unique(self, db_session: AsyncSession, test_user: User):
        """Test that email must be unique."""
        # Try to create another user with the same email
        user2 = User(
            api_key=str(uuid.uuid4()),
            name="Jane Doe",
            email=test_user.email,
        )
        db_session.add(user2)

        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            await db_session.commit()

    async def test_user_required_fields(self, db_session: AsyncSession):
        """Test that required fields cannot be null."""
        # Missing api_key
        user = User(name="Test", email="test@example.com")
        db_session.add(user)
        with pytest.raises(Exception):
            await db_session.commit()

        await db_session.rollback()

        # Missing name
        user = User(api_key=str(uuid.uuid4()), email="test@example.com")
        db_session.add(user)
        with pytest.raises(Exception):
            await db_session.commit()

        await db_session.rollback()

        # Missing email
        user = User(api_key=str(uuid.uuid4()), name="Test")
        db_session.add(user)
        with pytest.raises(Exception):
            await db_session.commit()

    async def test_user_without_email(self, db_session: AsyncSession):
        """Test creating user without email (optional field)."""
        user = User(
            api_key=str(uuid.uuid4()),
            name="No Email User",
        )
        db_session.add(user)
        await db_session.commit()

        assert user.email is None

    async def test_user_relationships(self, db_session: AsyncSession, test_user: User):
        """Test user relationships."""
        # Create a group owned by user
        group = Group(name="Test Group", owner_id=test_user.id)
        db_session.add(group)
        await db_session.commit()

        # Create a template for user
        template = Template(
            user_id=test_user.id,
            name="Test Template",
            config={"type": "even"},
        )
        db_session.add(template)
        await db_session.commit()

        # Load user with relationships
        result = await db_session.execute(select(User).where(User.id == test_user.id))
        user = result.scalar_one()

        assert len(user.groups) == 1
        assert len(user.templates) == 1


class TestGroupModel:
    """Test cases for Group model."""

    async def test_create_group(self, db_session: AsyncSession, test_user: User):
        """Test creating a group."""
        group_data = {
            "name": "Weekend Trip",
            "owner_id": test_user.id,
        }
        group = Group(**group_data)
        db_session.add(group)
        await db_session.commit()

        # Verify group was created
        result = await db_session.execute(
            select(Group).where(Group.name == "Weekend Trip")
        )
        saved_group = result.scalar_one()

        assert saved_group.name == "Weekend Trip"
        assert saved_group.owner_id == test_user.id
        assert saved_group.created_at is not None
        assert isinstance(saved_group.created_at, datetime)

    async def test_group_owner_relationship(
        self, db_session: AsyncSession, test_group: Group, test_user: User
    ):
        """Test group-owner relationship."""
        # Load group with owner
        result = await db_session.execute(
            select(Group).where(Group.id == test_group.id)
        )
        group = result.scalar_one()

        assert group.owner.id == test_user.id
        assert group.owner.name == test_user.name

    async def test_group_required_fields(self, db_session: AsyncSession):
        """Test that required fields cannot be null."""
        # Missing name
        group = Group(owner_id=1)
        db_session.add(group)
        with pytest.raises(Exception):
            await db_session.commit()

        await db_session.rollback()

        # Missing owner_id
        group = Group(name="Test Group")
        db_session.add(group)
        with pytest.raises(Exception):
            await db_session.commit()

    async def test_group_relationships(
        self, db_session: AsyncSession, testGroup: Group, test_user: User
    ):
        """Test group relationships."""
        # Add user as member
        member = GroupMember(group_id=testGroup.id, user_id=test_user.id)
        db_session.add(member)

        # Create a split for the group
        split = Split(
            group_id=testGroup.id,
            owner_id=test_user.id,
            receipt_data={"total": 100.0},
            split_results={"Test": 100.0},
            currency="USD",
        )
        db_session.add(split)
        await db_session.commit()

        # Load group with relationships
        result = await db_session.execute(select(Group).where(Group.id == testGroup.id))
        group = result.scalar_one()

        assert len(group.members) == 1
        assert len(group.splits) == 1


class TestGroupMemberModel:
    """Test cases for GroupMember model."""

    async def test_add_group_member(
        self, db_session: AsyncSession, test_group: Group, test_user: User
    ):
        """Test adding a member to a group."""
        # Create another user
        user2_data = {
            "api_key": str(uuid.uuid4()),
            "name": "Jane Doe",
            "email": "jane@example.com",
        }
        user2 = User(**user2_data)
        db_session.add(user2)
        await db_session.commit()

        # Add user2 to group
        member = GroupMember(group_id=test_group.id, user_id=user2.id)
        db_session.add(member)
        await db_session.commit()

        # Verify member was added
        result = await db_session.execute(
            select(GroupMember).where(
                GroupMember.group_id == test_group.id, GroupMember.user_id == user2.id
            )
        )
        saved_member = result.scalar_one()

        assert saved_member.group_id == test_group.id
        assert saved_member.user_id == user2.id
        assert saved_member.joined_at is not None
        assert isinstance(saved_member.joined_at, datetime)

    async def test_group_member_relationships(
        self, db_session: AsyncSession, test_group_member: GroupMember
    ):
        """Test group member relationships."""
        result = await db_session.execute(
            select(GroupMember).where(
                GroupMember.group_id == test_group_member.group_id
            )
        )
        member = result.scalar_one()

        assert member.group is not None
        assert member.user is not None
        assert member.group.name == "Test Group"
        assert member.user.name == "Test User"

    async def test_duplicate_group_member(
        self, db_session: AsyncSession, test_group: Group, test_user: User
    ):
        """Test that a user cannot be added to a group twice."""
        member1 = GroupMember(group_id=test_group.id, user_id=test_user.id)
        db_session.add(member1)
        await db_session.commit()

        # Try to add the same user again
        member2 = GroupMember(group_id=test_group.id, user_id=test_user.id)
        db_session.add(member2)
        with pytest.raises(Exception):
            await db_session.commit()


class TestSplitModel:
    """Test cases for Split model."""

    async def test_create_split(
        self, db_session: AsyncSession, test_group: Group, test_user: User
    ):
        """Test creating a split."""
        split_data = {
            "group_id": test_group.id,
            "owner_id": test_user.id,
            "receipt_data": {
                "items": [{"name": "Pizza", "price": 20.0}],
                "total": 20.0,
            },
            "split_results": {"Test User": 20.0},
            "currency": "USD",
        }
        split = Split(**split_data)
        db_session.add(split)
        await db_session.commit()

        # Verify split was created
        result = await db_session.execute(
            select(Split).where(Split.group_id == test_group.id)
        )
        saved_split = result.scalar_one()

        assert saved_split.group_id == test_group.id
        assert saved_split.owner_id == test_user.id
        assert saved_split.currency == "USD"
        assert saved_split.receipt_data == split_data["receipt_data"]
        assert saved_split.split_results == split_data["split_results"]
        assert saved_split.created_at is not None

    async def test_split_relationships(
        self, db_session: AsyncSession, test_split: Split
    ):
        """Test split relationships."""
        result = await db_session.execute(
            select(Split).where(Split.id == test_split.id)
        )
        split = result.scalar_one()

        assert split.group is not None
        assert split.owner is not None
        assert split.group.name == "Test Group"
        assert split.owner.name == "Test User"

    async def test_split_status_values(
        self, db_session: AsyncSession, test_group: Group, test_user: User
    ):
        """Test split status values."""
        statuses = ["pending", "confirmed", "cancelled"]

        for status in statuses:
            split = Split(
                group_id=test_group.id,
                owner_id=test_user.id,
                receipt_data={"total": 100.0},
                split_results={"Test": 100.0},
                currency="USD",
                status=status,
            )
            db_session.add(split)

        await db_session.commit()

        # Verify all statuses were saved correctly
        result = await db_session.execute(select(Split))
        splits = result.scalars().all()

        saved_statuses = [s.status for s in splits]
        assert all(status in saved_statuses for status in statuses)

    async def test_split_default_status(
        self, db_session: AsyncSession, test_group: Group, test_user: User
    ):
        """Test split default status."""
        split = Split(
            group_id=test_group.id,
            owner_id=test_user.id,
            receipt_data={"total": 100.0},
            split_results={"Test": 100.0},
            currency="USD",
        )
        db_session.add(split)
        await db_session.commit()

        assert split.status == "pending"

    async def test_split_default_currency(
        self, db_session: AsyncSession, test_group: Group, test_user: User
    ):
        """Test split default currency."""
        split = Split(
            group_id=test_group.id,
            owner_id=test_user.id,
            receipt_data={},
            split_results={},
        )
        db_session.add(split)
        await db_session.commit()

        assert split.currency == "IDR"

    async def test_split_without_group(self, db_session: AsyncSession, test_user: User):
        """Test creating split without group (optional field)."""
        split = Split(
            owner_id=test_user.id,
            receipt_data={"total": 100.0},
            split_results={"Test": 100.0},
            currency="USD",
        )
        db_session.add(split)
        await db_session.commit()

        assert split.group_id is None

    async def test_split_payment_relationship(
        self, db_session: AsyncSession, test_split: Split
    ):
        """Test split-payment relationship."""
        payment = Payment(
            split_id=test_split.id,
            person_name="Test Person",
            amount=50.0,
            currency="USD",
        )
        db_session.add(payment)
        await db_session.commit()

        # Load split with payments
        result = await db_session.execute(
            select(Split).where(Split.id == test_split.id)
        )
        split = result.scalar_one()

        assert len(split.payments) == 1


class TestPaymentModel:
    """Test cases for Payment model."""

    async def test_create_payment(self, db_session: AsyncSession, test_split: Split):
        """Test creating a payment."""
        payment_data = {
            "split_id": test_split.id,
            "person_name": "John Doe",
            "amount": 38.0,
            "currency": "USD",
        }
        payment = Payment(**payment_data)
        db_session.add(payment)
        await db_session.commit()

        # Verify payment was created
        result = await db_session.execute(
            select(Payment).where(Payment.split_id == test_split.id)
        )
        saved_payment = result.scalar_one()

        assert saved_payment.split_id == test_split.id
        assert saved_payment.person_name == "John Doe"
        assert saved_payment.amount == 38.0
        assert saved_payment.currency == "USD"
        assert saved_payment.confirmed_at is None

    async def test_payment_relationship(
        self, db_session: AsyncSession, test_payment: Payment
    ):
        """Test payment relationship with split."""
        result = await db_session.execute(
            select(Payment).where(Payment.id == test_payment.id)
        )
        payment = result.scalar_one()

        assert payment.split is not None
        assert payment.split.id == test_payment.split_id

    async def test_payment_status_transition(
        self, db_session: AsyncSession, test_payment: Payment
    ):
        """Test payment status transition."""
        # Update status to confirmed
        test_payment.confirmed_at = datetime.utcnow()
        await db_session.commit()

        # Verify update
        result = await db_session.execute(
            select(Payment).where(Payment.id == test_payment.id)
        )
        payment = result.scalar_one()

        assert payment.confirmed_at is not None
        assert isinstance(payment.confirmed_at, datetime)

    async def test_payment_status_values(
        self, db_session: AsyncSession, test_split: Split
    ):
        """Test payment status values."""
        statuses = ["pending", "confirmed", "unpaid"]

        for status in statuses:
            payment = Payment(
                split_id=test_split.id,
                person_name=f"Person {status}",
                amount=10.0,
                currency="USD",
                status=status,
            )
            db_session.add(payment)

        await db_session.commit()

        # Verify all statuses were saved correctly
        result = await db_session.execute(select(Payment))
        payments = result.scalars().all()

        saved_statuses = [p.status for p in payments]
        assert all(status in saved_statuses for status in statuses)

    async def test_payment_default_status(
        self, db_session: AsyncSession, test_split: Split
    ):
        """Test payment default status."""
        payment = Payment(
            split_id=test_split.id,
            person_name="Test Person",
            amount=50.0,
            currency="USD",
        )
        db_session.add(payment)
        await db_session.commit()

        assert payment.status == "unpaid"

    async def test_payment_amount_variations(
        self, db_session: AsyncSession, test_split: Split
    ):
        """Test payment with different amount values."""
        # Zero amount
        payment1 = Payment(
            split_id=test_split.id,
            person_name="Zero",
            amount=0.0,
            currency="USD",
        )
        db_session.add(payment1)

        # Negative amount
        payment2 = Payment(
            split_id=test_split.id,
            person_name="Negative",
            amount=-10.0,
            currency="USD",
        )
        db_session.add(payment2)

        # Large amount
        payment3 = Payment(
            split_id=test_split.id,
            person_name="Large",
            amount=999999.99,
            currency="USD",
        )
        db_session.add(payment3)

        await db_session.commit()

        assert payment1.amount == 0.0
        assert payment2.amount == -10.0
        assert payment3.amount == 999999.99


class TestTemplateModel:
    """Test cases for Template model."""

    async def test_create_template(self, db_session: AsyncSession, test_user: User):
        """Test creating a template."""
        template_data = {
            "user_id": test_user.id,
            "name": "Dinner Template",
            "config": {
                "type": "even",
                "settings": {
                    "include_tax": True,
                    "include_tip": True,
                },
            },
        }
        template = Template(**template_data)
        db_session.add(template)
        await db_session.commit()

        # Verify template was created
        result = await db_session.execute(
            select(Template).where(Template.name == "Dinner Template")
        )
        saved_template = result.scalar_one()

        assert saved_template.user_id == test_user.id
        assert saved_template.name == "Dinner Template"
        assert saved_template.config == template_data["config"]
        assert saved_template.created_at is not None

    async def test_template_relationship(
        self, db_session: AsyncSession, test_template: Template
    ):
        """Test template relationship with user."""
        result = await db_session.execute(
            select(Template).where(Template.id == test_template.id)
        )
        template = result.scalar_one()

        assert template.user is not None
        assert template.user.id == test_template.user_id

    async def test_template_user_cascade(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test that templates are deleted when user is deleted."""
        # Create a template
        template = Template(
            user_id=test_user.id,
            name="Test Template",
            config={"type": "even"},
        )
        db_session.add(template)
        await db_session.commit()

        # Delete user
        await db_session.delete(test_user)
        await db_session.commit()

        # Verify template was also deleted
        result = await db_session.execute(select(Template))
        templates = result.scalars().all()
        assert len(templates) == 0

    async def test_template_complex_config(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test template with complex configuration."""
        config = {
            "type": "itemized",
            "settings": {
                "tax_calculation": "proportional",
                "tip_calculation": "percentage",
                "default_tax_rate": 0.08,
                "default_tip_rate": 0.18,
            },
            "rules": {
                "min_item_price": 0.01,
                "max_item_price": 10000.0,
                "require_item_name": True,
            },
        }

        template = Template(
            user_id=test_user.id,
            name="Complex Template",
            config=config,
        )
        db_session.add(template)
        await db_session.commit()

        assert template.config == config


class TestCurrencyRateModel:
    """Test cases for CurrencyRate model."""

    async def test_create_currency_rate(self, db_session: AsyncSession):
        """Test creating a currency rate."""
        rate_data = {
            "from_currency": "USD",
            "to_currency": "EUR",
            "rate": 0.85,
            "updated_at": datetime.utcnow(),
        }
        rate = CurrencyRate(**rate_data)
        db_session.add(rate)
        await db_session.commit()

        # Verify rate was created
        result = await db_session.execute(
            select(CurrencyRate).where(
                CurrencyRate.from_currency == "USD", CurrencyRate.to_currency == "EUR"
            )
        )
        saved_rate = result.scalar_one()

        assert saved_rate.from_currency == "USD"
        assert saved_rate.to_currency == "EUR"
        assert saved_rate.rate == 0.85
        assert saved_rate.updated_at is not None

    async def test_currency_rate_unique_pair(
        self, db_session: AsyncSession, test_currency_rate: CurrencyRate
    ):
        """Test that currency pair must be unique."""
        # Try to create another rate with same currency pair
        rate2 = CurrencyRate(
            from_currency=test_currency_rate.from_currency,
            to_currency=test_currency_rate.to_currency,
            rate=0.90,
            updated_at=datetime.utcnow(),
        )
        db_session.add(rate2)

        with pytest.raises(Exception):
            await db_session.commit()

    async def test_currency_rate_reverse_pair(
        self, db_session: AsyncSession, test_currency_rate: CurrencyRate
    ):
        """Test creating reverse currency pair."""
        # Create reverse pair (EUR to USD)
        rate = CurrencyRate(
            from_currency="EUR",
            to_currency="USD",
            rate=1.18,  # 1/0.85 ≈ 1.18
            updated_at=datetime.utcnow(),
        )
        db_session.add(rate)
        await db_session.commit()

        # Verify both rates exist
        result = await db_session.execute(
            select(CurrencyRate).where(
                (CurrencyRate.from_currency == "USD")
                | (CurrencyRate.from_currency == "EUR")
            )
        )
        rates = result.scalars().all()
        assert len(rates) == 2

    async def test_currency_rate_default_timestamp(self, db_session: AsyncSession):
        """Test currency rate default timestamp."""
        rate = CurrencyRate(
            from_currency="GBP",
            to_currency="USD",
            rate=1.25,
        )
        db_session.add(rate)
        await db_session.commit()

        assert rate.updated_at is not None
        assert isinstance(rate.updated_at, datetime)

    async def test_currency_rate_various_rates(self, db_session: AsyncSession):
        """Test currency rates with various values."""
        rates_data = [
            ("USD", "EUR", 0.85),
            ("USD", "GBP", 0.73),
            ("USD", "JPY", 110.0),
            ("EUR", "USD", 1.18),
            ("GBP", "USD", 1.37),
        ]

        for from_cur, to_cur, rate_value in rates_data:
            rate = CurrencyRate(
                from_currency=from_cur,
                to_currency=to_cur,
                rate=rate_value,
            )
            db_session.add(rate)

        await db_session.commit()

        result = await db_session.execute(select(CurrencyRate))
        rates = result.scalars().all()
        assert len(rates) == len(rates_data)
