"""empty message

Revision ID: ace256cb2fed
Revises: 805a95be2644
Create Date: 2020-03-08 17:43:57.354776

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ace256cb2fed'
down_revision = '805a95be2644'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # OK, OK! I adjusted them!!!!!!!!!!!!!!!!!!!!!
    op.rename_table('order', 'orders')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # OK, OK! I adjusted them!!!!!!!!!!!!!!!!!!!
    op.rename_table('orders', 'order')
    # ### end Alembic commands ###