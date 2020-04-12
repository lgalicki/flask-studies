"""empty message

Revision ID: 39e582f4a404
Revises: 76cd69f3dadf
Create Date: 2020-03-29 18:42:53.604276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39e582f4a404'
down_revision = '76cd69f3dadf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('join_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'join_date')
    # ### end Alembic commands ###