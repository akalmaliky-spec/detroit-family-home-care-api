"""Add clients table.

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-20

Mirrors the SQLAlchemy Client model defined in dfhc/app/models.py:
 - id (Integer, PK, indexed)
 - full_name (String, not null)
 - date_of_birth (String, nullable)
 - diagnosis (String, nullable)
 - address (String, nullable)
 - phone (String, nullable)
 - emergency_contact_name (String, nullable)
 - emergency_contact_phone (String, nullable)
 - medicaid_id (String, nullable)
 - is_active (Boolean, default True)
 - notes (String, nullable)
 - created_at (DateTime, default utcnow)
 - updated_at (DateTime, default utcnow, onupdate utcnow)
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("date_of_birth", sa.String(), nullable=True),
        sa.Column("diagnosis", sa.String(), nullable=True),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("emergency_contact_name", sa.String(), nullable=True),
        sa.Column("emergency_contact_phone", sa.String(), nullable=True),
        sa.Column("medicaid_id", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_clients_id"), "clients", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_clients_id"), table_name="clients")
    op.drop_table("clients")
