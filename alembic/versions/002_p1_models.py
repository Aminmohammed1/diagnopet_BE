"""P1 models: Add Offer, Coupon, CouponRedemption, DistancePricingConfig, BillingRecord

Revision ID: 002_p1_models
Revises: 001_p0_models
Create Date: 2025-01-02

This migration includes:
- Create Offer table
- Create Coupon table
- Create CouponRedemption table
- Create DistancePricingConfig table
- Create BillingRecord table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_p1_models'
down_revision = '001_p0_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migrations"""
    
    # Create Offer table
    op.create_table(
        'offers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('discount_type', sa.String(50), nullable=False),
        sa.Column('discount_value', sa.Float(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('event_tag', sa.String(100), nullable=True),
        sa.Column('applicable_tests', sa.Text(), nullable=True),
        sa.Column('minimum_order_value', sa.Float(), nullable=True),
        sa.Column('created_by_admin_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['created_by_admin_id'], ['staff.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_offers_name'), 'offers', ['name'], unique=True)
    op.create_index(op.f('ix_offers_start_date'), 'offers', ['start_date'], unique=False)
    op.create_index(op.f('ix_offers_end_date'), 'offers', ['end_date'], unique=False)
    
    # Create Coupon table
    op.create_table(
        'coupons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(100), nullable=False, unique=True),
        sa.Column('offer_id', sa.Integer(), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('max_uses', sa.Integer(), nullable=True),
        sa.Column('current_uses', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_uses_per_user', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_by_admin_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['offer_id'], ['offers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_admin_id'], ['staff.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coupons_code'), 'coupons', ['code'], unique=True)
    op.create_index(op.f('ix_coupons_offer_id'), 'coupons', ['offer_id'], unique=False)
    op.create_index(op.f('ix_coupons_start_date'), 'coupons', ['start_date'], unique=False)
    op.create_index(op.f('ix_coupons_end_date'), 'coupons', ['end_date'], unique=False)
    
    # Create CouponRedemption table
    op.create_table(
        'coupon_redemptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('coupon_id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('discount_amount', sa.Float(), nullable=False),
        sa.Column('redemption_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['coupon_id'], ['coupons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coupon_redemptions_coupon_id'), 'coupon_redemptions', ['coupon_id'], unique=False)
    op.create_index(op.f('ix_coupon_redemptions_booking_id'), 'coupon_redemptions', ['booking_id'], unique=False)
    op.create_index(op.f('ix_coupon_redemptions_user_id'), 'coupon_redemptions', ['user_id'], unique=False)
    op.create_index(op.f('ix_coupon_redemptions_redemption_date'), 'coupon_redemptions', ['redemption_date'], unique=False)
    
    # Create DistancePricingConfig table
    op.create_table(
        'distance_pricing_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('base_charge', sa.Float(), nullable=False),
        sa.Column('charge_per_km', sa.Float(), nullable=False),
        sa.Column('max_free_distance_km', sa.Float(), nullable=False),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_until', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('updated_by_admin_id', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['updated_by_admin_id'], ['staff.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_distance_pricing_configs_effective_from'), 'distance_pricing_configs', ['effective_from'], unique=False)
    
    # Create BillingRecord table
    op.create_table(
        'billing_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('test_ids', sa.Text(), nullable=True),
        sa.Column('base_amount', sa.Float(), nullable=False),
        sa.Column('discount_amount', sa.Float(), nullable=False, server_default='0'),
        sa.Column('distance_charge', sa.Float(), nullable=False, server_default='0'),
        sa.Column('final_amount', sa.Float(), nullable=False),
        sa.Column('billing_date', sa.Date(), nullable=False),
        sa.Column('billing_period', sa.String(10), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('invoice_number', sa.String(100), nullable=True, unique=True),
        sa.Column('invoice_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paid_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_billing_records_booking_id'), 'billing_records', ['booking_id'], unique=False)
    op.create_index(op.f('ix_billing_records_user_id'), 'billing_records', ['user_id'], unique=False)
    op.create_index(op.f('ix_billing_records_billing_date'), 'billing_records', ['billing_date'], unique=False)
    op.create_index(op.f('ix_billing_records_status'), 'billing_records', ['status'], unique=False)


def downgrade() -> None:
    """Revert migrations"""
    
    # Drop BillingRecord table
    op.drop_table('billing_records')
    
    # Drop DistancePricingConfig table
    op.drop_table('distance_pricing_configs')
    
    # Drop CouponRedemption table
    op.drop_table('coupon_redemptions')
    
    # Drop Coupon table
    op.drop_table('coupons')
    
    # Drop Offer table
    op.drop_table('offers')
