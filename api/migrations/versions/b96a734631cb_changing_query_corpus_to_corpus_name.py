"""Changing Query.corpus to corpus_name

Revision ID: b96a734631cb
Revises: 75ad232e76b9
Create Date: 2017-08-28 14:36:06.282785

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b96a734631cb'
down_revision = '75ad232e76b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('query', sa.Column('corpus_name', sa.String(length=254), nullable=True))
    op.drop_column('query', 'corpus')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('query', sa.Column('corpus', mysql.VARCHAR(length=254), nullable=True))
    op.drop_column('query', 'corpus_name')
    # ### end Alembic commands ###
