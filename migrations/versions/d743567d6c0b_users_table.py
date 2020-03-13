"""users table

Revision ID: d743567d6c0b
Revises: e6c508c31df7
Create Date: 2020-03-10 22:07:18.303893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd743567d6c0b'
down_revision = 'e6c508c31df7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('file', 'path')
    op.add_column('user', sa.Column('drive_folder_id', sa.String(length=512), nullable=True))
    op.add_column('user', sa.Column('first_name', sa.String(length=128), nullable=True))
    op.add_column('user', sa.Column('last_name', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_name')
    op.drop_column('user', 'first_name')
    op.drop_column('user', 'drive_folder_id')
    op.add_column('file', sa.Column('path', sa.VARCHAR(length=2048), nullable=True))
    # ### end Alembic commands ###
