"""remove_cascade_from_address_fk

Revision ID: 20260123000002
Revises: 20260123000001
Create Date: 2026-01-23 00:00:02.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260123000002'
down_revision: Union[str, Sequence[str], None] = '20260123000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the old foreign key with CASCADE
    op.drop_constraint('fk_bookings_address_id', 'bookings', type_='foreignkey')
    
    # Create new foreign key without CASCADE
    op.create_foreign_key('fk_bookings_address_id', 'bookings', 'addresses', ['address_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the foreign key without CASCADE
    op.drop_constraint('fk_bookings_address_id', 'bookings', type_='foreignkey')
    
    # Recreate with CASCADE
    op.create_foreign_key('fk_bookings_address_id', 'bookings', 'addresses', ['address_id'], ['id'], ondelete='CASCADE')
