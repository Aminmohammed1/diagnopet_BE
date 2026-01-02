# Database Schema Evolution Plan

## 📋 Overview

This document outlines all database schema changes required to support the development roadmap (P0 → P3). Changes are organized by priority and dependency.

---

## 🔴 P0 — CRITICAL SCHEMA CHANGES

### Core Entity Relationships (HIGHEST PRIORITY)

#### 1. **ADD: Pet Model** ❌ MISSING

**Purpose:** Store user's pets (one user → multiple pets)

```python
# NEW TABLE: pets
class Pet(Base):
    __tablename__ = "pets"
    
    id: int (PK)
    user_id: int (FK → users.id) [CASCADE]
    name: str (required, indexed)
    species: str (e.g., "Dog", "Cat", "Bird")
    breed: str | None
    age_years: float | None
    weight_kg: float | None
    medical_history: str | None (text field)
    is_active: bool (default=True)
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    user: User (back_populates="pets")
    bookings: List[Booking] (back_populates="pet")
    reports: List[TestReport] (back_populates="pet")
```

**Why:** Currently, **no pet tracking exists**. User → Booking is 1:M, but bookings don't track which pet was tested.

**Migration Script Needed:**
- Add `pet_id` column to `bookings` table
- Make `pet_id` nullable initially for existing bookings
- Create default pet for each user based on existing bookings

---

#### 2. **ADD: TestReport Model** ❌ MISSING

**Purpose:** Store test results with per-booking traceability

```python
# NEW TABLE: test_reports
class TestReport(Base):
    __tablename__ = "test_reports"
    
    id: int (PK)
    booking_item_id: int (FK → booking_items.id) [CASCADE] (unique, indexed)
    pet_id: int (FK → pets.id) [CASCADE] (indexed)
    test_id: int (FK → tests.id) [CASCADE] (indexed)
    batch_group_id: int | None (FK → test_batch_groups.id) (for multi-test grouping)
    
    # Report content
    report_file_url: str | None (PDF/image storage in Supabase)
    findings: str | None (text field - doctor's findings)
    status: str (default="pending", options: pending|generated|verified|delivered)
    
    # Timestamps
    created_at: datetime
    generated_at: datetime | None
    delivered_at: datetime | None
    updated_at: datetime
    
    # Relationships
    booking_item: BookingItem (back_populates="report")
    pet: Pet (back_populates="reports")
    test: Test
    batch_group: TestBatchGroup | None (back_populates="reports")
```

**Why:** Reports must be traceable per booking + per pet. One test in a booking = one report.

---

#### 3. **ADD: TestBatchGroup Model** ⚠️ NEW

**Purpose:** Group multiple tests/reports for bulk operations (optional for P0, critical for P1 analytics)

```python
# NEW TABLE: test_batch_groups
class TestBatchGroup(Base):
    __tablename__ = "test_batch_groups"
    
    id: int (PK)
    booking_id: int (FK → bookings.id) [CASCADE] (indexed)
    
    # Batch metadata
    batch_name: str | None (e.g., "Wellness Panel 2025-01-02")
    description: str | None
    
    # Timing
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    booking: Booking (back_populates="batch_groups")
    reports: List[TestReport] (back_populates="batch_group")
```

**Why:** Enables grouping of tests created in same booking (e.g., "Full Health Panel") for admin billing & analytics.

---

#### 4. **MODIFY: Booking Model**

**Current Issues:**
- ❌ No `pet_id` → can't track which pet was tested
- ❌ No `batch_group_id` → no test grouping

**Add Columns:**

```python
class Booking(Base):
    __tablename__ = "bookings"
    
    # EXISTING FIELDS (keep as-is)
    id: int
    user_id: int
    booking_date: datetime
    status: str
    address: str
    address_link: str
    created_at: datetime
    updated_at: datetime
    
    # NEW FIELDS
    pet_id: int (FK → pets.id) [CASCADE] (indexed)
    collection_staff_id: int | None (FK → staff.id) (for tracking who collected)
    notes: str | None (special instructions)
    estimated_distance_km: float | None (for home visit charges)
    
    # Relationships
    pet: Pet (back_populates="bookings")
    collection_staff: Staff | None
    batch_groups: List[TestBatchGroup] (back_populates="booking")
```

**Migration:**
```sql
ALTER TABLE bookings 
ADD COLUMN pet_id INTEGER;
ALTER TABLE bookings 
ADD FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE;

-- Create default pet for each user
INSERT INTO pets (user_id, name, species, created_at, updated_at)
SELECT id, CONCAT('Pet_', id), 'Unknown', NOW(), NOW()
FROM users;

-- Assign bookings to user's first pet
UPDATE bookings b
SET pet_id = (SELECT id FROM pets WHERE user_id = b.user_id LIMIT 1);

-- Make pet_id NOT NULL
ALTER TABLE bookings MODIFY COLUMN pet_id INTEGER NOT NULL;
```

---

#### 5. **MODIFY: BookingItem Model**

**Current Issue:**
- ❌ No test report tracking

**Add Columns:**

```python
class BookingItem(Base):
    __tablename__ = "booking_items"
    
    # EXISTING
    id: int
    booking_id: int
    test_id: int
    
    # NEW
    quantity: int (default=1, for bulk orders)
    unit_price: float (price at time of booking)
    status: str (default="pending", options: pending|collected|processing|completed)
    
    # Relationships
    report: TestReport | None (back_populates="booking_item", one-to-one)
    booking: Booking
    test: Test
```

**Migration:**
```sql
ALTER TABLE booking_items ADD COLUMN quantity INTEGER DEFAULT 1;
ALTER TABLE booking_items ADD COLUMN unit_price NUMERIC(10, 2);
ALTER TABLE booking_items ADD COLUMN status VARCHAR(50) DEFAULT 'pending';
```

---

#### 6. **ADD: Staff Model** ❌ MISSING

**Purpose:** Track staff members (collectors, lab techs, admins) with roles

```python
# NEW TABLE: staff
class Staff(Base):
    __tablename__ = "staff"
    
    id: int (PK)
    name: str (indexed)
    phone: str (unique, indexed)
    email: str | None (unique)
    hashed_password: str
    
    # Role & permissions
    role: str (indexed, enum: admin|collector|lab_tech|analyst)
    is_active: bool (default=True)
    
    # Location (for collector routing)
    assigned_area: str | None (e.g., "Downtown", "Suburbs")
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    collections: List[Booking] (back_populates="collection_staff")
```

**Why:** Admin, collectors, and lab techs need separate login + role-based access control.

---

### Authentication & Session Management

#### 7. **ADD: Session/Token Blacklist** (Optional but Recommended)

**Purpose:** Handle page refresh during checkout without re-asking login

```python
# NEW TABLE: token_blacklist (for logout)
class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"
    
    id: int (PK)
    token: str (unique, indexed)
    user_id: int (FK → users.id)
    created_at: datetime
    expires_at: datetime
```

**Or use Redis for short-lived session tokens** (preferred for scalability).

**Why:** Allows checking if a token is still valid during checkout completion without re-authentication.

---

#### 8. **MODIFY: User Model**

**Current Issues:**
- ❌ No `role` variants for staff (currently just "USER"/"ADMIN")
- ✅ Has `is_verified` but needs better session handling

**Add Columns:**

```python
class User(Base):
    __tablename__ = "users"
    
    # EXISTING (keep)
    id: int
    phone: str
    email: str
    hashed_password: str
    full_name: str | None
    is_active: bool
    is_superuser: bool
    is_verified: bool
    role: str (currently "USER")
    
    # NEW (optional, for better auth tracking)
    last_login: datetime | None
    login_attempts: int (default=0, reset after successful login)
    is_locked: bool (default=False, lock after 5 failed attempts)
    
    # Relationships
    pets: List[Pet] (back_populates="user")
    bookings: List[Booking] (back_populates="user")
    addresses: List[Address] (back_populates="user")
```

---

## 🟠 P1 — HIGH PRIORITY SCHEMA CHANGES

### Admin Operations & Billing

#### 9. **ADD: Offer Model** ❌ MISSING

**Purpose:** Create & manage promotional offers

```python
# NEW TABLE: offers
class Offer(Base):
    __tablename__ = "offers"
    
    id: int (PK)
    name: str (unique, indexed)
    description: str | None
    discount_type: str (enum: percentage|fixed_amount)
    discount_value: float
    
    # Validity
    start_date: date (indexed)
    end_date: date (indexed)
    is_active: bool (default=True)
    
    # Targeting
    event_tag: str | None (e.g., "Christmas", "New Year", "Health Month")
    applicable_tests: str | None (JSON: ["test_id_1", "test_id_2"] or "all")
    minimum_order_value: float | None
    
    # Tracking
    created_at: datetime
    created_by_admin_id: int | None
    updated_at: datetime
    
    # Relationships
    coupons: List[Coupon] (back_populates="offer")
```

---

#### 10. **ADD: Coupon Model** ❌ MISSING

**Purpose:** Redemption codes for offers

```python
# NEW TABLE: coupons
class Coupon(Base):
    __tablename__ = "coupons"
    
    id: int (PK)
    code: str (unique, indexed)
    offer_id: int (FK → offers.id) [CASCADE] (nullable for independent coupons)
    
    # Validity
    start_date: datetime (indexed)
    end_date: datetime (indexed)
    is_active: bool (default=True)
    
    # Usage limits
    max_uses: int | None (null = unlimited)
    current_uses: int (default=0)
    max_uses_per_user: int (default=1)
    
    # Tracking
    created_at: datetime
    created_by_admin_id: int | None
    
    # Relationships
    offer: Offer | None (back_populates="coupons")
    redemptions: List[CouponRedemption] (back_populates="coupon")
```

---

#### 11. **ADD: CouponRedemption Model** ❌ MISSING

**Purpose:** Track coupon usage per booking

```python
# NEW TABLE: coupon_redemptions
class CouponRedemption(Base):
    __tablename__ = "coupon_redemptions"
    
    id: int (PK)
    coupon_id: int (FK → coupons.id) [CASCADE] (indexed)
    booking_id: int (FK → bookings.id) [CASCADE] (indexed)
    user_id: int (FK → users.id) [CASCADE] (indexed)
    
    discount_amount: float
    redemption_date: datetime (indexed)
    
    # Relationships
    coupon: Coupon (back_populates="redemptions")
    booking: Booking
    user: User
```

---

#### 12. **MODIFY: Test Model**

**Current Issues:**
- ❌ Missing tube type & quantity (ml)
- ❌ No sample collection instructions

**Add Columns:**

```python
class Test(Base):
    __tablename__ = "tests"
    
    # EXISTING
    id: int
    category_id: int
    name: str
    description: str | None
    price: float
    discounted_price: float | None
    sample_type: str | None
    report_time_hours: int | None
    is_active: bool
    
    # NEW
    tube_type: str | None (e.g., "EDTA", "SST", "Heparin")
    sample_quantity_ml: float | None (e.g., 2.0, 5.0)
    sample_collection_instructions: str | None (text field)
    
    # Metadata
    tat_hours: int | None (turnaround time, alias for report_time_hours)
    created_at: datetime (if not present)
    updated_at: datetime (if not present)
```

**Migration:**
```sql
ALTER TABLE tests ADD COLUMN tube_type VARCHAR(100);
ALTER TABLE tests ADD COLUMN sample_quantity_ml NUMERIC(5, 2);
ALTER TABLE tests ADD COLUMN sample_collection_instructions TEXT;
ALTER TABLE tests ADD COLUMN created_at DATETIME;
ALTER TABLE tests ADD COLUMN updated_at DATETIME;
```

---

#### 13. **ADD: DistancePricingConfig Model** ❌ MISSING

**Purpose:** Admin management of distance-based home visit charges

```python
# NEW TABLE: distance_pricing_configs
class DistancePricingConfig(Base):
    __tablename__ = "distance_pricing_configs"
    
    id: int (PK)
    
    # Pricing structure
    base_charge: float (e.g., 50 INR)
    charge_per_km: float (e.g., 5 INR/km)
    max_free_distance_km: float (e.g., 2 km free, then charges apply)
    
    # Validity
    effective_from: date (indexed)
    effective_until: date | None
    is_active: bool (default=True)
    
    # Tracking
    updated_by_admin_id: int | None
    updated_at: datetime
    created_at: datetime
```

**Why:** Admin can update pricing without code changes. Multiple configs can be created to track pricing history.

---

#### 14. **ADD: Billing Record Model** ❌ MISSING

**Purpose:** Track day-wise/month-wise billing for reconciliation

```python
# NEW TABLE: billing_records
class BillingRecord(Base):
    __tablename__ = "billing_records"
    
    id: int (PK)
    booking_id: int (FK → bookings.id) [CASCADE] (indexed)
    user_id: int (FK → users.id) [CASCADE] (indexed)
    
    # Test & pricing
    test_ids: str (JSON: list of test IDs)
    base_amount: float
    discount_amount: float (from offers/coupons)
    distance_charge: float
    final_amount: float
    
    # Billing period
    billing_date: date (indexed)
    billing_period: str (e.g., "2025-01")
    
    # Status
    status: str (enum: draft|finalized|invoiced|paid)
    invoice_number: str | None (unique)
    invoice_date: datetime | None
    paid_date: datetime | None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    booking: Booking
    user: User
```

---

## 🟡 P2 — MEDIUM PRIORITY SCHEMA CHANGES

#### 15. **ADD: PrescriptionUpload Model** ❌ MISSING

**Purpose:** Store uploaded prescriptions/test forms during booking

```python
# NEW TABLE: prescription_uploads
class PrescriptionUpload(Base):
    __tablename__ = "prescription_uploads"
    
    id: int (PK)
    booking_id: int (FK → bookings.id) [CASCADE] (indexed)
    user_id: int (FK → users.id) [CASCADE] (indexed)
    
    # File metadata
    file_url: str (Supabase storage)
    file_name: str
    file_type: str (e.g., "application/pdf", "image/jpeg")
    file_size_bytes: int
    
    # Upload tracking
    uploaded_at: datetime (indexed)
    verified_by_admin_id: int | None
    verification_notes: str | None
    
    # Relationships
    booking: Booking
    user: User
    verified_by: Staff | None
```

**Why:** Admins can verify prescriptions during booking processing, improving accuracy.

---

#### 16. **ADD: ClinicInfo Model** ⚠️ NEW

**Purpose:** Store clinic details for WhatsApp & Maps links (single record)

```python
# NEW TABLE: clinic_info
class ClinicInfo(Base):
    __tablename__ = "clinic_info"
    
    id: int (PK) [only 1 record]
    
    # Contact
    whatsapp_number: str (with country code, e.g., "+91XXXXXXXXXX")
    whatsapp_link: str (generated link)
    
    # Location
    clinic_address: str
    google_maps_link: str
    latitude: float | None
    longitude: float | None
    
    # Hours
    opening_time: time | None (e.g., "09:00")
    closing_time: time | None (e.g., "18:00")
    
    # Updated by admin
    updated_by_admin_id: int | None
    updated_at: datetime
```

**Why:** Single source for clinic contact info. Easy for UI to fetch and display.

---

## 🟢 P3 — LOW PRIORITY SCHEMA CHANGES

*(No schema changes required for P3 features — they reuse existing models)*

---

## 📊 ER Diagram (Proposed Final State)

```
┌─────────────────┐
│     USERS       │
├─────────────────┤
│ id (PK)         │
│ phone           │◄──┐
│ email           │   │
│ role            │   │
│ created_at      │   │
└─────────────────┘   │
         ▲            │
         │            │
    ┌────┴────────────┼────────────────┐
    │                 │                │
    │                 │                │
┌──────────────┐      │        ┌──────────────┐
│    PETS      │      │        │   BOOKINGS   │
├──────────────┤      │        ├──────────────┤
│ id (PK)      │      └────────│ user_id (FK) │
│ user_id (FK) │               │ pet_id (FK)  │
│ name         │      ┌────────│ status       │
│ species      │      │        │ created_at   │
└──────────────┘      │        └──────────────┘
         │            │              │
         │            │              │
         │     ┌──────┴───────────────┼────────────────┐
         │     │                      │                │
         │     │                      │                │
    ┌────┴────┴──────────────┐   ┌─────────────────┐  │
    │    BOOKING_ITEMS       │   │  TEST_REPORTS   │  │
    ├────────────────────────┤   ├─────────────────┤  │
    │ id (PK)                │   │ id (PK)         │  │
    │ booking_id (FK)        │   │ booking_item_id │  │
    │ test_id (FK)───────────┼───│ (FK, unique)    │  │
    │ quantity               │   │ pet_id (FK)─────┼──┘
    │ status                 │   │ status          │
    └────────────────────────┘   │ report_file_url │
                                 │ created_at      │
                                 └─────────────────┘

┌──────────────────┐
│    TESTS         │
├──────────────────┤
│ id (PK)          │
│ category_id (FK) │
│ name             │
│ price            │
│ tube_type        │
│ sample_qty_ml    │
│ collection_instr │
└──────────────────┘

┌──────────────────┐
│   ADDRESSES      │
├──────────────────┤
│ id (PK)          │
│ user_id (FK)     │
│ address_line1    │
│ city             │
│ postal_code      │
│ is_default       │
└──────────────────┘

┌──────────────────┐
│    STAFF         │
├──────────────────┤
│ id (PK)          │
│ name             │
│ phone            │
│ role             │
│ is_active        │
└──────────────────┘

┌──────────────────┐
│    OFFERS        │
├──────────────────┤
│ id (PK)          │
│ name             │
│ discount_type    │
│ discount_value   │
│ start_date       │
│ end_date         │
│ is_active        │
└──────────────────┘

┌──────────────────┐
│    COUPONS       │
├──────────────────┤
│ id (PK)          │
│ code             │
│ offer_id (FK)    │
│ max_uses         │
│ current_uses     │
└──────────────────┘
```

---

## 📋 Migration Checklist

### Phase 1: P0 Models (Critical)
- [ ] Create `Pet` model
- [ ] Create `TestReport` model
- [ ] Create `TestBatchGroup` model
- [ ] Create `Staff` model
- [ ] Modify `Booking` to add `pet_id`, `collection_staff_id`, `notes`, `estimated_distance_km`
- [ ] Modify `BookingItem` to add `quantity`, `unit_price`, `status`
- [ ] Modify `Test` to add tube_type, sample_quantity_ml, sample_collection_instructions
- [ ] Modify `User` (optional: add last_login, login_attempts, is_locked)
- [ ] Create migration scripts for data backfill

### Phase 2: P1 Models (High Priority)
- [ ] Create `Offer` model
- [ ] Create `Coupon` model
- [ ] Create `CouponRedemption` model
- [ ] Create `DistancePricingConfig` model
- [ ] Create `BillingRecord` model

### Phase 3: P2 Models (Medium Priority)
- [ ] Create `PrescriptionUpload` model
- [ ] Create `ClinicInfo` model

### Phase 4: API Endpoints
- [ ] CRUD endpoints for each new model
- [ ] Bulk operations (billing export, offer management)
- [ ] Search/filter endpoints

---

## 🔧 Implementation Notes

### Database Strategy
- Use **SQLAlchemy ORM** (already in place)
- Use **Alembic** for migrations (already set up)
- Test migrations locally before production

### Performance Considerations
- Add **indexes** on frequently queried columns (FK, date ranges, status)
- Denormalize `billing_records.test_ids` as JSON for quick filtering
- Consider **materialized views** for complex billing queries

### Data Integrity
- Use **CASCADE deletes** for ownership relationships (e.g., Pet→Booking)
- Use **SET NULL** for optional relationships (e.g., collection_staff_id)
- Add **unique constraints** where needed (coupon codes, email)

### API Changes Required
- All reports endpoints must now filter by `pet_id`
- Booking creation must include `pet_id`
- Admin endpoints need staff role checks
- New endpoints for staff login, offer management, billing

---

## 📝 Summary of Changes by Entity

| Entity | Change | Type | P0 | P1 | P2 | P3 |
|--------|--------|------|----|----|----|----|
| **User** | Add session tracking | Modify | ✓ |  |  |  |
| **Pet** | Create new model | Add | ✓ |  |  |  |
| **Booking** | Add pet_id, staff_id, notes | Modify | ✓ |  |  |  |
| **BookingItem** | Add quantity, status | Modify | ✓ |  |  |  |
| **Test** | Add tube_type, sample_qty, instructions | Modify | ✓ |  |  |  |
| **TestReport** | Create new model | Add | ✓ |  |  |  |
| **TestBatchGroup** | Create new model | Add | ✓ |  |  |  |
| **Staff** | Create new model | Add | ✓ |  |  |  |
| **Offer** | Create new model | Add |  | ✓ |  |  |
| **Coupon** | Create new model | Add |  | ✓ |  |  |
| **CouponRedemption** | Create new model | Add |  | ✓ |  |  |
| **DistancePricingConfig** | Create new model | Add |  | ✓ |  |  |
| **BillingRecord** | Create new model | Add |  | ✓ |  |  |
| **PrescriptionUpload** | Create new model | Add |  |  | ✓ |  |
| **ClinicInfo** | Create new model | Add |  |  | ✓ |  |

---

## 🎯 Next Steps

1. **Review & Approve** this schema plan with stakeholders
2. **Create Alembic migrations** for P0 models
3. **Update CRUD operations** for modified models
4. **Update API schemas** (Pydantic) to match new DB models
5. **Update API endpoints** to enforce new relationships
6. **Write integration tests** for new relationships
7. **Document API contracts** for frontend team

---

**Last Updated:** January 2, 2025  
**Status:** Ready for Review
