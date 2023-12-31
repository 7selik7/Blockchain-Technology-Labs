"""change item

Revision ID: 50677a9849b8
Revises: 1cb19e965a08
Create Date: 2023-11-22 20:48:20.095928

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50677a9849b8'
down_revision: Union[str, None] = '1cb19e965a08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('blocks', 'id',
               existing_type=sa.BIGINT(),
               type_=sa.String(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('blocks', 'id',
               existing_type=sa.String(),
               type_=sa.BIGINT(),
               existing_nullable=False)
    # ### end Alembic commands ###
