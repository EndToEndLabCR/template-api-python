"""initial_user_model_with_role

Revision ID: 62c5f367a69b
Revises:
Create Date: 2026-06-17 23:48:46.184198

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "62c5f367a69b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("first_name", sa.String(50), nullable=False),
        sa.Column("last_name", sa.String(50), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="viewer"),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("password_reset_token_hash", sa.String(255), nullable=True),
        sa.Column("password_reset_expires_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
