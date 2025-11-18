"""Add unique constraint to users username

Revision ID: 4d39d0783769
Revises: b687896de460
Create Date: 2025-11-17 12:58:17.272021

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d39d0783769'
down_revision: Union[str, Sequence[str], None] = 'b687896de460'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
