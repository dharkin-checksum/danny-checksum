"""create monitored_slack_channels table

Revision ID: a1b2c3d4e5f6
Revises: cac0e65b6965
Create Date: 2026-02-21 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'cac0e65b6965'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('monitored_slack_channels',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('channel_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('channel_id')
    )
    # Seed with the existing channel
    op.execute(
        "INSERT INTO monitored_slack_channels (channel_id, name) "
        "VALUES ('C0AFX0Y4U1M', 'checksum-danny')"
    )


def downgrade() -> None:
    op.drop_table('monitored_slack_channels')
