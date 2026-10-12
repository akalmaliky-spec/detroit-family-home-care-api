"""Add revocable sessions and explicit client ownership."""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("token_version", sa.Integer(), server_default="0", nullable=False))
    with op.batch_alter_table("clients") as batch:
        batch.add_column(sa.Column("owner_user_id", sa.Integer(), nullable=True))
        batch.create_foreign_key("fk_clients_owner_user_id", "users", ["owner_user_id"], ["id"], ondelete="SET NULL")
        batch.create_index("ix_clients_owner_user_id", ["owner_user_id"])
    op.create_table("refresh_sessions",
        sa.Column("token_hash", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_refresh_sessions_user_id", "refresh_sessions", ["user_id"])


def downgrade():
    op.drop_table("refresh_sessions")
    with op.batch_alter_table("clients") as batch:
        batch.drop_index("ix_clients_owner_user_id")
        batch.drop_constraint("fk_clients_owner_user_id", type_="foreignkey")
        batch.drop_column("owner_user_id")
    with op.batch_alter_table("users") as batch:
        batch.drop_column("token_version")
