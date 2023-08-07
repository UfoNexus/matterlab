"""add table mattermost channel

Revision ID: 517bd853da12
Revises: f6f1bd85935d
Create Date: 2023-08-07 11:56:29.942753

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '517bd853da12'
down_revision = 'f6f1bd85935d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gitlab_project_mattermost_channel',
    sa.Column('gitlab_project_id', sa.Integer(), nullable=False),
    sa.Column('mattermost_channel_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['gitlab_project_id'], ['gitlab_project.id'], ),
    sa.ForeignKeyConstraint(['mattermost_channel_id'], ['mattermost_channel.id'], ),
    sa.PrimaryKeyConstraint('gitlab_project_id', 'mattermost_channel_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('gitlab_project_mattermost_channel')
    # ### end Alembic commands ###