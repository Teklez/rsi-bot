"""fix_user_symbols_sequence

Revision ID: fix_user_symbols_seq
Revises: a5d363a74f27
Create Date: 2025-09-29 09:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_user_symbols_seq'
down_revision: Union[str, Sequence[str], None] = 'a5d363a74f27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create sequence for user_symbols.id
    op.execute("CREATE SEQUENCE IF NOT EXISTS user_symbols_id_seq")
    op.execute("ALTER TABLE user_symbols ALTER COLUMN id SET DEFAULT nextval('user_symbols_id_seq')")
    op.execute("ALTER SEQUENCE user_symbols_id_seq OWNED BY user_symbols.id")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE user_symbols ALTER COLUMN id DROP DEFAULT")
    op.execute("DROP SEQUENCE IF EXISTS user_symbols_id_seq")
