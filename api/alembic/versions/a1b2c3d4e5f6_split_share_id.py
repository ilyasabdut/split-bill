"""add splits.share_id for public share links, make owner_id optional

Revision ID: a1b2c3d4e5f6
Revises: 3352fc82e057
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "3352fc82e057"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("splits", sa.Column("share_id", sa.String(length=32), nullable=True))
    op.create_unique_constraint("uq_splits_share_id", "splits", ["share_id"])
    op.alter_column("splits", "owner_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.alter_column("splits", "owner_id", existing_type=sa.Integer(), nullable=False)
    op.drop_constraint("uq_splits_share_id", "splits", type_="unique")
    op.drop_column("splits", "share_id")
