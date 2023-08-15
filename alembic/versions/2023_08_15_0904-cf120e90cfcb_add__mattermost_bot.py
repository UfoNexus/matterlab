"""add__mattermost_bot

Revision ID: cf120e90cfcb
Revises: 16a24b7389c9
Create Date: 2023-08-15 09:04:19.819280

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf120e90cfcb'
down_revision = '16a24b7389c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mattermost_bot',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('iid', sa.String(), nullable=False),
    sa.Column('access_token', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('mattermost_bot')
    # ### end Alembic commands ###