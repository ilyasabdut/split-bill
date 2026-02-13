from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    api_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    groups: Mapped[List["Group"]] = relationship(back_populates="owner")
    templates: Mapped[List["Template"]] = relationship(back_populates="user")


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner: Mapped["User"] = relationship(back_populates="groups")
    members: Mapped[List["User"]] = relationship(secondary="group_members")
    splits: Mapped[List["Split"]] = relationship(back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_members"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Split(Base):
    __tablename__ = "splits"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("groups.id"))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    receipt_data: Mapped[dict] = mapped_column(JSON)
    split_results: Mapped[dict] = mapped_column(JSON)
    currency: Mapped[str] = mapped_column(String(10), default="IDR")
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    group: Mapped[Optional["Group"]] = relationship(back_populates="splits")
    payments: Mapped[List["Payment"]] = relationship(back_populates="split")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    split_id: Mapped[int] = mapped_column(ForeignKey("splits.id"))
    person_name: Mapped[str] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(50), default="unpaid")
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    split: Mapped["Split"] = relationship(back_populates="payments")


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))
    config: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="templates")


class CurrencyRate(Base):
    __tablename__ = "currency_rates"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_currency: Mapped[str] = mapped_column(String(10))
    to_currency: Mapped[str] = mapped_column(String(10))
    rate: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
