"""empty message

Revision ID: 8660a1cfaa7a
Revises: 
Create Date: 2021-10-07 09:21:23.709098

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8660a1cfaa7a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('articles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=True),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('authors', sa.String(length=200), nullable=True),
    sa.Column('source', sa.String(length=100), nullable=True),
    sa.Column('url', sa.String(length=200), nullable=True),
    sa.Column('artdate', sa.Date(), nullable=True),
    sa.Column('briefingdate', sa.Date(), nullable=False),
    sa.Column('ranking', sa.Integer(), nullable=False),
    sa.Column('nextart', sa.Integer(), nullable=True),
    sa.Column('prevart', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('articles')
    # ### end Alembic commands ###
