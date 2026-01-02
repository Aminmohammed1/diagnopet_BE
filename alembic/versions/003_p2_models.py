"""P2 models: Add PrescriptionUpload and ClinicInfo

Revision ID: 003_p2_models
Revises: 002_p1_models
Create Date: 2025-01-02

This migration includes:
- Create PrescriptionUpload table
- Create ClinicInfo table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_p2_models'
down_revision = '002_p1_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migrations"""
    
    # Create PrescriptionUpload table
    op.create_table(
        'prescription_uploads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('file_url', sa.Text(), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_type', sa.String(100), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('verified_by_admin_id', sa.Integer(), nullable=True),
        sa.Column('verification_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['verified_by_admin_id'], ['staff.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prescription_uploads_booking_id'), 'prescription_uploads', ['booking_id'], unique=False)
    op.create_index(op.f('ix_prescription_uploads_user_id'), 'prescription_uploads', ['user_id'], unique=False)
    op.create_index(op.f('ix_prescription_uploads_uploaded_at'), 'prescription_uploads', ['uploaded_at'], unique=False)
    
    # Create ClinicInfo table
    op.create_table(
        'clinic_info',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('whatsapp_number', sa.String(50), nullable=False),
        sa.Column('whatsapp_link', sa.Text(), nullable=True),
        sa.Column('clinic_address', sa.Text(), nullable=False),
        sa.Column('google_maps_link', sa.Text(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('opening_time', sa.Time(), nullable=True),
        sa.Column('closing_time', sa.Time(), nullable=True),
        sa.Column('updated_by_admin_id', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['updated_by_admin_id'], ['staff.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Revert migrations"""
    
    # Drop ClinicInfo table
    op.drop_table('clinic_info')
    
    # Drop PrescriptionUpload table
    op.drop_table('prescription_uploads')
