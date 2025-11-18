"""Add unique constraint to users username

Revision ID: 72c4487a8e41
Revises: 94c3c65231c9
Create Date: 2025-11-17 13:05:29.699928

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72c4487a8e41'
down_revision: Union[str, Sequence[str], None] = '94c3c65231c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
