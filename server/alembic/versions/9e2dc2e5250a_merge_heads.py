"""merge heads

Revision ID: 9e2dc2e5250a
Revises: 024e1f42c42f, 8b2b7b3ae81a
Create Date: 2025-08-18 05:35:57.317728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e2dc2e5250a'
down_revision: Union[str, None] = ('024e1f42c42f', '8b2b7b3ae81a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
