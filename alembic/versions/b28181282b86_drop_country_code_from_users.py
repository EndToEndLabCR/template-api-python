"""Drop country_code column from users

Revision ID: b28181282b86
Revises: dc7ae61a4084
Create Date: 2026-05-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b28181282b86'
down_revision: Union[str, None] = 'dc7ae61a4084'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('users', 'country_code')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('users', sa.Column('country_code', sa.String(length=10), nullable=True))
