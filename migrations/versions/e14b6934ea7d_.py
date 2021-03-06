"""empty message

Revision ID: e14b6934ea7d
Revises: 43d625d1532e
Create Date: 2020-09-25 15:10:32.304978

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e14b6934ea7d'
down_revision = '43d625d1532e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('event_fee_uix_event_id_member_type_id', 'event_fee', ['event_id', 'member_type_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('event_fee_uix_event_id_member_type_id', 'event_fee', type_='unique')
    # ### end Alembic commands ###
