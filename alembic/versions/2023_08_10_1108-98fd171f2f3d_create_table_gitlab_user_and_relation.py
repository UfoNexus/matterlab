"""create_table_gitlab_user_and_relation

Revision ID: 98fd171f2f3d
Revises: 2037b8e981c1
Create Date: 2023-08-10 11:08:27.773514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98fd171f2f3d'
down_revision = '2037b8e981c1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gitlab_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('iid', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('access_token', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('iid')
    )
    op.create_index(op.f('ix_gitlab_user_access_token'), 'gitlab_user', ['access_token'], unique=False)
    op.add_column('mattermost_user', sa.Column('gitlab_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'mattermost_user', 'gitlab_user', ['gitlab_user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'mattermost_user', type_='foreignkey')
    op.drop_column('mattermost_user', 'gitlab_user_id')
    op.drop_index(op.f('ix_gitlab_user_access_token'), table_name='gitlab_user')
    op.drop_table('gitlab_user')
    # ### end Alembic commands ###
