from fastapi import APIRouter
from api.v1.endpoints import tests, users, login_register, bookings, reports, addresses, pet, geolocation, categories, orders

api_router = APIRouter()
api_router.include_router(tests.router, prefix="/tests", tags=["tests"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(login_register.router, prefix="/auth", tags=["auth"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(addresses.router, prefix="/addresses", tags=["addresses"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(pet.router, prefix="/pets", tags=["pets"])
api_router.include_router(geolocation.router, tags=["geolocation"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])