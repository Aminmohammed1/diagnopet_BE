# API Endpoints Implementation Roadmap

**Status:** Schema complete, API development ready

---

## P0 Priority Endpoints

### User & Pet Management
```
POST   /api/v1/users/{user_id}/pets
  - Create new pet for user
  - Input: name, species, breed, age, weight, medical_history
  - Output: Pet object

GET    /api/v1/users/{user_id}/pets
  - List all pets for user
  - Output: List[Pet]

GET    /api/v1/pets/{pet_id}
  - Get pet details
  - Output: Pet object

PUT    /api/v1/pets/{pet_id}
  - Update pet information
  - Input: Pet fields
  - Output: Pet object

DELETE /api/v1/pets/{pet_id}
  - Delete pet (soft delete recommended)
```

### Booking & Test Reports
```
POST   /api/v1/bookings
  - Create booking with pet_id
  - Input: user_id, pet_id, booking_date, items[], address
  - Output: Booking object with items

GET    /api/v1/bookings/{booking_id}
  - Get booking details with items
  - Output: Booking object

PUT    /api/v1/bookings/{booking_id}
  - Update booking status
  - Input: status, notes
  - Output: Booking object

GET    /api/v1/users/{user_id}/bookings
  - Get user's bookings (all pets)
  - Query: date_from, date_to, status
  - Output: List[Booking]

GET    /api/v1/pets/{pet_id}/reports
  - Get test reports for specific pet (P0 requirement)
  - Query: date_from, date_to, status
  - Output: List[TestReport]

POST   /api/v1/booking-items/{booking_item_id}/report
  - Create/upload test report
  - Input: report_file_url, findings, status
  - Output: TestReport object

GET    /api/v1/reports/{report_id}
  - Get report details
  - Output: TestReport object

PUT    /api/v1/reports/{report_id}
  - Update report status/findings
  - Input: findings, status
  - Output: TestReport object

DELETE /api/v1/reports/{report_id}
  - Delete/archive report
```

### Staff & Authentication
```
POST   /api/v1/auth/staff/login
  - Staff login
  - Input: phone, password
  - Output: JWT token

POST   /api/v1/staff
  - Create staff member (admin only)
  - Input: name, phone, email, password, role, assigned_area
  - Output: Staff object

GET    /api/v1/staff
  - List all staff (admin only)
  - Query: role, is_active
  - Output: List[Staff]

GET    /api/v1/staff/{staff_id}
  - Get staff details

PUT    /api/v1/staff/{staff_id}
  - Update staff info (admin only)

DELETE /api/v1/staff/{staff_id}
  - Deactivate staff (soft delete)
```

---

## P1 Priority Endpoints

### Offer Management
```
POST   /api/v1/admin/offers
  - Create offer (admin only)
  - Input: name, description, discount_type, discount_value, dates, event_tag
  - Output: Offer object

GET    /api/v1/admin/offers
  - List all offers
  - Query: is_active, event_tag
  - Output: List[Offer]

GET    /api/v1/admin/offers/{offer_id}
  - Get offer details

PUT    /api/v1/admin/offers/{offer_id}
  - Update offer

DELETE /api/v1/admin/offers/{offer_id}
  - Deactivate offer

GET    /api/v1/offers/active
  - Get active offers for user (non-admin)
  - Output: List[Offer]
```

### Coupon Management
```
POST   /api/v1/admin/coupons
  - Create coupon (admin only)
  - Input: code, offer_id, start_date, end_date, max_uses
  - Output: Coupon object

GET    /api/v1/admin/coupons
  - List all coupons with usage stats
  - Query: code, offer_id, is_active
  - Output: List[Coupon]

POST   /api/v1/bookings/{booking_id}/apply-coupon
  - Apply coupon to booking
  - Input: coupon_code
  - Output: CouponRedemption object + updated booking total

GET    /api/v1/bookings/{booking_id}/coupon
  - Get applied coupon details

DELETE /api/v1/bookings/{booking_id}/coupon
  - Remove coupon from booking
```

### Billing
```
GET    /api/v1/admin/billing?date_from=&date_to=&period=month
  - Get billing report
  - Query: date_from, date_to, period (day/month/custom)
  - Output: List[BillingRecord]

POST   /api/v1/admin/billing/generate
  - Generate billing for period (admin only)
  - Input: billing_period
  - Output: List[BillingRecord]

GET    /api/v1/admin/billing/{billing_id}
  - Get billing record details

PUT    /api/v1/admin/billing/{billing_id}/status
  - Update billing status (draft → finalized → invoiced → paid)
  - Input: status
  - Output: BillingRecord object

GET    /api/v1/admin/billing/export?format=csv|pdf
  - Export billing records
```

### Distance Pricing
```
POST   /api/v1/admin/distance-pricing
  - Create distance pricing config (admin only)
  - Input: base_charge, charge_per_km, max_free_distance, effective_from
  - Output: DistancePricingConfig

GET    /api/v1/admin/distance-pricing
  - Get current and historical pricing
  - Output: List[DistancePricingConfig]

PUT    /api/v1/admin/distance-pricing/{config_id}
  - Update pricing config

POST   /api/v1/bookings/{booking_id}/calculate-distance
  - Calculate distance from clinic to address (OpenStreetMap/Google Maps)
  - Input: address coordinates or address string
  - Output: { distance_km, charge }
```

---

## P2 Priority Endpoints

### Prescription Uploads
```
POST   /api/v1/bookings/{booking_id}/prescription
  - Upload prescription/form
  - Input: file (multipart), file_name, file_type
  - Output: PrescriptionUpload object

GET    /api/v1/bookings/{booking_id}/prescriptions
  - List prescriptions for booking

GET    /api/v1/prescription/{prescription_id}
  - Get prescription details

PUT    /api/v1/prescription/{prescription_id}/verify
  - Admin verify prescription (admin only)
  - Input: verification_notes, status
  - Output: PrescriptionUpload object

DELETE /api/v1/prescription/{prescription_id}
  - Delete prescription
```

### Clinic Info
```
GET    /api/v1/clinic-info
  - Get clinic information (public endpoint)
  - Output: ClinicInfo object

PUT    /api/v1/admin/clinic-info
  - Update clinic info (admin only)
  - Input: address, phone, hours, location, links

POST   /api/v1/clinic-info/whatsapp
  - Generate WhatsApp link (public)
  - Output: { whatsapp_link }

POST   /api/v1/clinic-info/maps
  - Get maps link (public)
  - Output: { maps_link }
```

---

## Admin Dashboard Endpoints (P1)

### Daily View / Booking Management
```
GET    /api/v1/admin/bookings?date=YYYY-MM-DD
  - Get all bookings for date
  - Query: date, status (pending/collected/completed)
  - Output: List[Booking] with status breakdown

PUT    /api/v1/admin/bookings/{booking_id}/status
  - Update booking status
  - Input: status, collection_staff_id (if assigning collector)
  - Output: Booking object

GET    /api/v1/admin/dashboard/daily-stats?date=YYYY-MM-DD
  - Dashboard stats for day
  - Output: {
      total_bookings: number,
      by_status: { pending, collected, completed },
      total_tests: number,
      total_revenue: number
    }
```

### Test CRUD
```
POST   /api/v1/admin/tests
  - Create test (admin only)
  - Input: name, description, price, category, tube_type, sample_qty, instructions
  - Output: Test object

GET    /api/v1/admin/tests
  - List tests
  - Query: category_id, is_active
  - Output: List[Test]

GET    /api/v1/tests/{test_id}
  - Get test details (public)

PUT    /api/v1/admin/tests/{test_id}
  - Update test info (admin only)

DELETE /api/v1/admin/tests/{test_id}
  - Deactivate test (soft delete)

GET    /api/v1/tests/categories
  - Get test categories (public)
```

---

## Authentication & Authorization

### Middleware Requirements
```
✓ Token validation on all /admin/* routes
✓ Role-based access control (admin, collector, lab_tech, user)
✓ Pet ownership validation (users see only their pets)
✓ Staff assignment validation
```

### Headers
```
Authorization: Bearer <JWT_TOKEN>
X-User-ID: {user_id} (extracted from token)
```

---

## Response Standards

### Success (200, 201)
```json
{
  "success": true,
  "data": { /* object */ },
  "message": "Operation successful"
}
```

### Error (4xx, 5xx)
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { /* optional */ }
  }
}
```

### Pagination
```json
{
  "data": [ /* array */ ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 100,
    "pages": 5
  }
}
```

---

## Implementation Order (Recommended)

### Phase 1 (Week 1)
1. User & Pet endpoints
2. Basic Booking CRUD
3. Staff authentication

### Phase 2 (Week 2)
1. TestReport endpoints
2. Admin Test CRUD
3. Daily booking view

### Phase 3 (Week 3)
1. Offer & Coupon system
2. Coupon application to booking
3. Distance calculation

### Phase 4 (Week 4)
1. Billing generation & export
2. Prescription uploads
3. Clinic info management

---

**Ready to start API development!**
