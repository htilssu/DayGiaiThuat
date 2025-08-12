"""
update exercises fields: drop constraint/suggest, add title/category/estimated_time/completion_rate/completed/content/code_template

Revision ID: fe12ab34cd56
Revises: ec640e77e236
Create Date: 2025-08-12 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fe12ab34cd56"
down_revision = "ec640e77e236"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns
    op.add_column("exercises", sa.Column("title", sa.String(), server_default="", nullable=False))
    op.add_column("exercises", sa.Column("category", sa.String(), nullable=True))
    op.add_column("exercises", sa.Column("estimated_time", sa.String(), nullable=True))
    op.add_column("exercises", sa.Column("completion_rate", sa.Integer(), nullable=True))
    op.add_column("exercises", sa.Column("completed", sa.Boolean(), nullable=True))
    op.add_column("exercises", sa.Column("content", sa.Text(), nullable=True))
    op.add_column("exercises", sa.Column("code_template", sa.Text(), nullable=True))

    # Make name nullable to match model (backward-compatible)
    try:
        op.alter_column("exercises", "name", existing_type=sa.String(), nullable=True)
    except Exception:
        pass

    # Drop legacy columns
    with op.batch_alter_table("exercises") as batch_op:
        try:
            batch_op.drop_column("constraint")
        except Exception:
            pass
        try:
            batch_op.drop_column("suggest")
        except Exception:
            pass

    # Remove server default from title after data backfill (if necessary)
    op.alter_column("exercises", "title", server_default=None)


def downgrade() -> None:
    # Recreate legacy columns
    op.add_column("exercises", sa.Column("suggest", sa.String(), nullable=True))
    op.add_column("exercises", sa.Column("constraint", sa.String(), nullable=True))

    # Drop new columns
    with op.batch_alter_table("exercises") as batch_op:
        for col in [
            "code_template",
            "content",
            "completed",
            "completion_rate",
            "estimated_time",
            "category",
            "title",
        ]:
            try:
                batch_op.drop_column(col)
            except Exception:
                pass

    # Make name non-nullable again (best effort)
    try:
        op.alter_column("exercises", "name", existing_type=sa.String(), nullable=False)
    except Exception:
        pass


