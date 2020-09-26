"""empty message

Revision ID: e344bec3ada7
Revises: d45cc2a4a837
Create Date: 2020-09-16 16:07:48.259359

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e344bec3ada7'
down_revision = 'd45cc2a4a837'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event_attend_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('attend_date', sa.ARRAY(sa.DateTime()), nullable=True),
    sa.Column('papers', sa.Boolean(), nullable=True),
    sa.Column('attend_social_gathering', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'event_id', name='uix_user_id_event_id')
    )
    op.drop_table('event_user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event_user',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('event_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('attend_date', postgresql.ARRAY(postgresql.TIMESTAMP()), autoincrement=False, nullable=True),
    sa.Column('papers', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('attend_social_gathering', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], name='event_user_event_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='event_user_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='event_user_pkey'),
    sa.UniqueConstraint('user_id', 'event_id', name='uix_user_id_event_id')
    )
    op.drop_table('event_attend_user')
    # ### end Alembic commands ###
