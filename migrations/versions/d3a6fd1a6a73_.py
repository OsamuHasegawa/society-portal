"""empty message

Revision ID: d3a6fd1a6a73
Revises: e14b6934ea7d
Create Date: 2020-09-25 15:25:14.810866

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3a6fd1a6a73'
down_revision = 'e14b6934ea7d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event_attend_user', sa.Column('payment_status', sa.TEXT(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('event_attend_user', 'payment_status')
    # ### end Alembic commands ###
