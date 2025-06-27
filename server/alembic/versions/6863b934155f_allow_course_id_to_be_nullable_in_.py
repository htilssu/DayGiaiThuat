"""allow course_id to be nullable in topics table

Revision ID: 6863b934155f
Revises: 25b0924d37a7
Create Date: 2025-06-26 21:26:39.230217

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6863b934155f"
down_revision: Union[str, None] = "25b0924d37a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Thay đổi cột course_id từ NOT NULL thành nullable
    op.alter_column("topics", "course_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    # Quay lại trạng thái NOT NULL (chỉ khi tất cả course_id đều không NULL)
    op.alter_column("topics", "course_id", existing_type=sa.Integer(), nullable=False)
