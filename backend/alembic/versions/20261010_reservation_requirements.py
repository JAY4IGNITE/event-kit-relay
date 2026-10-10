"""Persist reservation requirements for idempotent request comparison."""
from alembic import op
import sqlalchemy as sa

revision = "20261010_requirements"
down_revision = "f0093f424d11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("reservations", sa.Column("required_types", sa.JSON(), nullable=False,
                                           server_default="[]"))


def downgrade() -> None:
    op.drop_column("reservations", "required_types")
