"""Add unique constraint to users username

Revision ID: 3e6b22f9bdd2
Revises: 4d39d0783769
Create Date: 2025-11-17 13:01:52.949537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e6b22f9bdd2'
down_revision: Union[str, Sequence[str], None] = '4d39d0783769'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
