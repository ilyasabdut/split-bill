"""anonymous device identity, unique currency pair, cascade user templates

Revision ID: b7e1c2d3f4a5
Revises: a1b2c3d4e5f6
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b7e1c2d3f4a5"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("device_id", sa.String(length=36), nullable=True))
    op.create_unique_constraint("uq_users_device_id", "users", ["device_id"])
    # keep the newest row per pair so the constraint can be added on live data
    op.execute(
        "DELETE FROM currency_rates a USING currency_rates b "
        "WHERE a.from_currency = b.from_currency AND a.to_currency = b.to_currency "
        "AND (a.updated_at, a.id) < (b.updated_at, b.id)"
    )
    op.create_unique_constraint(
        "uq_currency_rates_pair", "currency_rates", ["from_currency", "to_currency"]
    )
    op.drop_constraint("templates_user_id_fkey", "templates", type_="foreignkey")
    op.create_foreign_key(
        "templates_user_id_fkey",
        "templates",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("templates_user_id_fkey", "templates", type_="foreignkey")
    op.create_foreign_key(
        "templates_user_id_fkey", "templates", "users", ["user_id"], ["id"]
    )
    op.drop_constraint("uq_currency_rates_pair", "currency_rates", type_="unique")
    op.drop_constraint("uq_users_device_id", "users", type_="unique")
    op.drop_column("users", "device_id")
