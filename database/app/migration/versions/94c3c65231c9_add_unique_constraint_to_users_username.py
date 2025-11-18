"""Add unique constraint to users username

Revision ID: 94c3c65231c9
Revises: 3e6b22f9bdd2
Create Date: 2025-11-17 13:03:21.388885

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94c3c65231c9'
down_revision: Union[str, Sequence[str], None] = '3e6b22f9bdd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
