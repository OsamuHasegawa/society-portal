"""empty message

Revision ID: 07e22764a3f4
Revises: 784ac2987b64
Create Date: 2020-09-08 03:00:48.285379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07e22764a3f4'
down_revision = '784ac2987b64'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('member',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('state',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.TEXT(), nullable=True),
    sa.Column('email', sa.TEXT(), nullable=False),
    sa.Column('password', sa.TEXT(), nullable=False),
    sa.Column('role', sa.Integer(), nullable=False),
    sa.Column('state', sa.Integer(), nullable=False),
    sa.Column('token', sa.TEXT(), nullable=True),
    sa.Column('token_period', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['role'], ['role.id'], ),
    sa.ForeignKeyConstraint(['state'], ['state.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_profile',
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('member_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.TEXT(), nullable=False),
    sa.Column('last_name', sa.TEXT(), nullable=False),
    sa.Column('first_name_kana', sa.TEXT(), nullable=False),
    sa.Column('last_name_kana', sa.TEXT(), nullable=False),
    sa.Column('organization', sa.TEXT(), nullable=False),
    sa.Column('department', sa.TEXT(), nullable=True),
    sa.Column('address_type', sa.Integer(), nullable=False),
    sa.Column('zip', sa.Integer(), nullable=False),
    sa.Column('prefecture', sa.Integer(), nullable=False),
    sa.Column('municipalities', sa.TEXT(), nullable=False),
    sa.Column('address1', sa.TEXT(), nullable=False),
    sa.Column('address2', sa.TEXT(), nullable=True),
    sa.Column('phone', sa.TEXT(), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['member_id'], ['member.id'], ),
    sa.PrimaryKeyConstraint('account_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_profile')
    op.drop_table('user')
    op.drop_table('state')
    op.drop_table('role')
    op.drop_table('member')
    # ### end Alembic commands ###
