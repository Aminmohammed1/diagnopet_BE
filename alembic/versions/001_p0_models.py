"""P0 models: Add Pet, TestReport, TestBatchGroup, Staff and modify existing models

Revision ID: 001_p0_models
Revises: 
Create Date: 2025-01-02

This migration includes:
- Create Pet table
- Create TestReport table
- Create TestBatchGroup table
- Create Staff table
- Modify User table (add session tracking)
- Modify Booking table (add pet_id, collection_staff_id, notes, estimated_distance_km)
- Modify BookingItem table (add quantity, unit_price, status)
- Modify Test table (add tube_type, sample_quantity_ml, sample_collection_instructions, tat_hours, timestamps)
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_p0_models'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migrations"""
    
    # Create Pet table
    op.create_table(
        'pets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('species', sa.String(100), nullable=False),
        sa.Column('breed', sa.String(100), nullable=True),
        sa.Column('age_years', sa.Float(), nullable=True),
        sa.Column('weight_kg', sa.Float(), nullable=True),
        sa.Column('medical_history', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pets_user_id'), 'pets', ['user_id'], unique=False)
    op.create_index(op.f('ix_pets_name'), 'pets', ['name'], unique=False)
    
    # Create Staff table
    op.create_table(
        'staff',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(255), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=True, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('assigned_area', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_staff_name'), 'staff', ['name'], unique=False)
    op.create_index(op.f('ix_staff_phone'), 'staff', ['phone'], unique=True)
    op.create_index(op.f('ix_staff_role'), 'staff', ['role'], unique=False)
    
    # Modify User table - add new columns
    op.add_column('users', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('login_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='false'))
    
    # Modify Booking table - add new columns
    op.add_column('bookings', sa.Column('pet_id', sa.Integer(), nullable=False))
    op.add_column('bookings', sa.Column('collection_staff_id', sa.Integer(), nullable=True))
    op.add_column('bookings', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('bookings', sa.Column('estimated_distance_km', sa.Float(), nullable=True))
    
    # Add foreign keys for Booking
    op.create_foreign_key('fk_bookings_pet_id', 'bookings', 'pets', ['pet_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_bookings_staff_id', 'bookings', 'staff', ['collection_staff_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('ix_bookings_pet_id'), 'bookings', ['pet_id'], unique=False)
    
    # Modify BookingItem table - add new columns
    op.add_column('booking_items', sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('booking_items', sa.Column('unit_price', sa.Numeric(10, 2), nullable=False, server_default='0'))
    op.add_column('booking_items', sa.Column('status', sa.String(50), nullable=False, server_default='pending'))
    
    # Modify Test table - add new columns
    op.add_column('tests', sa.Column('tube_type', sa.String(100), nullable=True))
    op.add_column('tests', sa.Column('sample_quantity_ml', sa.Numeric(5, 2), nullable=True))
    op.add_column('tests', sa.Column('sample_collection_instructions', sa.Text(), nullable=True))
    op.add_column('tests', sa.Column('tat_hours', sa.Integer(), nullable=True))
    op.add_column('tests', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column('tests', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()))
    
    # Create TestBatchGroup table
    op.create_table(
        'test_batch_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('batch_name', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_batch_groups_booking_id'), 'test_batch_groups', ['booking_id'], unique=False)
    
    # Create TestReport table
    op.create_table(
        'test_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_item_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('pet_id', sa.Integer(), nullable=False),
        sa.Column('test_id', sa.Integer(), nullable=False),
        sa.Column('batch_group_id', sa.Integer(), nullable=True),
        sa.Column('report_file_url', sa.Text(), nullable=True),
        sa.Column('findings', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['booking_item_id'], ['booking_items.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pet_id'], ['pets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['test_id'], ['tests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['batch_group_id'], ['test_batch_groups.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_reports_booking_item_id'), 'test_reports', ['booking_item_id'], unique=True)
    op.create_index(op.f('ix_test_reports_pet_id'), 'test_reports', ['pet_id'], unique=False)
    op.create_index(op.f('ix_test_reports_test_id'), 'test_reports', ['test_id'], unique=False)
    op.create_index(op.f('ix_test_reports_batch_group_id'), 'test_reports', ['batch_group_id'], unique=False)
    op.create_index(op.f('ix_test_reports_status'), 'test_reports', ['status'], unique=False)


def downgrade() -> None:
    """Revert migrations"""
    
    # Drop TestReport table
    op.drop_table('test_reports')
    
    # Drop TestBatchGroup table
    op.drop_table('test_batch_groups')
    
    # Remove Test table columns
    op.drop_column('tests', 'updated_at')
    op.drop_column('tests', 'created_at')
    op.drop_column('tests', 'tat_hours')
    op.drop_column('tests', 'sample_collection_instructions')
    op.drop_column('tests', 'sample_quantity_ml')
    op.drop_column('tests', 'tube_type')
    
    # Remove BookingItem columns
    op.drop_column('booking_items', 'status')
    op.drop_column('booking_items', 'unit_price')
    op.drop_column('booking_items', 'quantity')
    
    # Remove Booking foreign keys and columns
    op.drop_index('ix_bookings_pet_id', table_name='bookings')
    op.drop_constraint('fk_bookings_staff_id', 'bookings', type_='foreignkey')
    op.drop_constraint('fk_bookings_pet_id', 'bookings', type_='foreignkey')
    op.drop_column('bookings', 'estimated_distance_km')
    op.drop_column('bookings', 'notes')
    op.drop_column('bookings', 'collection_staff_id')
    op.drop_column('bookings', 'pet_id')
    
    # Remove User columns
    op.drop_column('users', 'is_locked')
    op.drop_column('users', 'login_attempts')
    op.drop_column('users', 'last_login')
    
    # Drop Staff table
    op.drop_table('staff')
    
    # Drop Pet table
    op.drop_table('pets')
