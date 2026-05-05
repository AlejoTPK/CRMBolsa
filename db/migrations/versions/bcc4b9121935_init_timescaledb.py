"""Init TimescaleDB

Revision ID: bcc4b9121935
Revises: 
Create Date: 2026-05-02 00:07:37.290892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bcc4b9121935'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Ensure TimescaleDB extension exists
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
    
    # 2. Create the market_ticks table
    op.create_table(
        'market_ticks',
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('timestamp', 'symbol')
    )
    
    # 3. Create index for the symbol (Timescale automatically creates index on the time column)
    op.create_index(op.f('ix_market_ticks_symbol'), 'market_ticks', ['symbol'], unique=False)
    
    # 4. Convert the table into a TimescaleDB hypertable
    # The 'timestamp' column is used for partitioning
    op.execute("SELECT create_hypertable('market_ticks', by_range('timestamp'));")


def downgrade() -> None:
    # Drop the table (this automatically drops the hypertable configuration)
    op.drop_index(op.f('ix_market_ticks_symbol'), table_name='market_ticks')
    op.drop_table('market_ticks')
