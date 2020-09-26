"""empty message

Revision ID: 2cba5a38b554
Revises: d3a6fd1a6a73
Create Date: 2020-09-25 20:52:16.925392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2cba5a38b554'
down_revision = 'd3a6fd1a6a73'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_profile', sa.Column('member_type_id', sa.Integer(), nullable=False))
    op.drop_constraint('user_profile_member_id_fkey', 'user_profile', type_='foreignkey')
    op.create_foreign_key(None, 'user_profile', 'member_type', ['member_type_id'], ['id'])
    op.drop_column('user_profile', 'member_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_profile', sa.Column('member_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'user_profile', type_='foreignkey')
    op.create_foreign_key('user_profile_member_id_fkey', 'user_profile', 'member_type', ['member_id'], ['id'])
    op.drop_column('user_profile', 'member_type_id')
    # ### end Alembic commands ###
