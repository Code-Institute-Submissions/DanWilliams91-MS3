"""empty message

Revision ID: 447dca615a3b
Revises: 681b5f06b0cb
Create Date: 2022-08-02 18:22:55.677467

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '447dca615a3b'
down_revision = '681b5f06b0cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('name', sa.Column('img_url', sa.String()))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'favourites')
    # ### end Alembic commands ###
