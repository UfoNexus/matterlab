"""add table gitlab project

Revision ID: c40ee8c0eabb
Revises: 
Create Date: 2023-08-07 11:33:41.812758

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c40ee8c0eabb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gitlab_project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gitlab_project_name'), 'gitlab_project', ['name'], unique=False)
    op.create_index(op.f('ix_gitlab_project_url'), 'gitlab_project', ['url'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_gitlab_project_url'), table_name='gitlab_project')
    op.drop_index(op.f('ix_gitlab_project_name'), table_name='gitlab_project')
    op.drop_table('gitlab_project')
    # ### end Alembic commands ###