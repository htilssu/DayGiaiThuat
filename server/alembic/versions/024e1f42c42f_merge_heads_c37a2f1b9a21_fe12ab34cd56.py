"""merge heads c37a2f1b9a21 + fe12ab34cd56

Revision ID: 024e1f42c42f
Revises: c37a2f1b9a21, fe12ab34cd56
Create Date: 2025-08-12 15:15:56.784137

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '024e1f42c42f'
down_revision: Union[str, None] = ('c37a2f1b9a21', 'fe12ab34cd56')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
