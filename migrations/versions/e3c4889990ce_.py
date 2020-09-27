"""empty message

Revision ID: e3c4889990ce
Revises: 07e22764a3f4
Create Date: 2020-09-11 02:38:43.541495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3c4889990ce'
down_revision = '07e22764a3f4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('member', sa.Column('label', sa.TEXT(), nullable=False))
    op.alter_column('member', 'name',
               existing_type=sa.TEXT(),
               nullable=False)
    op.alter_column('role', 'name',
               existing_type=sa.TEXT(),
               nullable=False)
    op.alter_column('state', 'name',
               existing_type=sa.TEXT(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('state', 'name',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('role', 'name',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('member', 'name',
               existing_type=sa.TEXT(),
               nullable=True)
    op.drop_column('member', 'label')
    # ### end Alembic commands ###