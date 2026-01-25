"""replace_address_columns_with_fk

Revision ID: 20260123000001
Revises: 4161f35561c1
Create Date: 2026-01-23 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260123000001'
down_revision: Union[str, Sequence[str], None] = '4161f35561c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add the new address_id foreign key column
    op.add_column('bookings', sa.Column('address_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_bookings_address_id', 'bookings', 'addresses', ['address_id'], ['id'])
    op.create_index(op.f('ix_bookings_address_id'), 'bookings', ['address_id'], unique=False)
    
    # Drop the old columns
    op.drop_column('bookings', 'address_link')
    op.drop_column('bookings', 'address')


def downgrade() -> None:
    """Downgrade schema."""
    # Add back the old columns
    op.add_column('bookings', sa.Column('address', sa.String(255), nullable=True))
    op.add_column('bookings', sa.Column('address_link', sa.String(255), nullable=True))
    
    # Drop the new foreign key and column
    op.drop_index(op.f('ix_bookings_address_id'), 'bookings')
    op.drop_constraint('fk_bookings_address_id', 'bookings', type_='foreignkey')
    op.drop_column('bookings', 'address_id')
