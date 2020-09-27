"""empty message

Revision ID: c69a27dd50b3
Revises: e344bec3ada7
Create Date: 2020-09-16 16:09:01.389837

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c69a27dd50b3'
down_revision = 'e344bec3ada7'
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
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('event_attend_user')
    # ### end Alembic commands ###