"""merge branches

Revision ID: 47ad36ff4d24
Revises: 7d256c53b2a5, 5cde50f49a21
Create Date: 2025-07-08 17:06:46.161081

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '47ad36ff4d24'
down_revision: Union[str, None] = ('7d256c53b2a5', '5cde50f49a21')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
