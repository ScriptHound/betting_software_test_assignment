"""empty message

Revision ID: c152ea2f2e95
Revises: 
Create Date: 2023-09-24 05:23:29.105460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c152ea2f2e95"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bets",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("event_id", sa.String(), nullable=True),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.Column(
            "status", sa.Enum("NEW", "WIN", "LOSE", name="betstatus"), nullable=True
        ),
    )


def downgrade() -> None:
    op.drop_table("bets")
