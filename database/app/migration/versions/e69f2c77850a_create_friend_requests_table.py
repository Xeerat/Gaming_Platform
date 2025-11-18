"""Create friend_requests table

Revision ID: e69f2c77850a
Revises: 8b94e9f2a64d
Create Date: 2025-11-17 12:29:47.310178

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e69f2c77850a'
down_revision: Union[str, Sequence[str], None] = '8b94e9f2a64d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
