"""scrypt

Revision ID: ef7e9730e23d
Revises: eece2ac2e460
Create Date: 2023-06-30 03:22:29.131934

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'ef7e9730e23d'
down_revision = 'eece2ac2e460'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'password',
               existing_type=mysql.VARCHAR(length=100),
               type_=sa.String(length=170),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'password',
               existing_type=sa.String(length=170),
               type_=mysql.VARCHAR(length=100),
               existing_nullable=True)
    # ### end Alembic commands ###
