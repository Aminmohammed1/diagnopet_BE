from fastapi import APIRouter
import httpx

router = APIRouter()

@router.get("/geocode")
async def geocode(q: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": q,
                "format": "json"
            },
            headers={
                "User-Agent": "Diagnopet/1.0 (diagnopet.com)"
            }
        )
        return res.json()
    
@router.get("/reverse-geocode")
async def reverse_geocode(lat: float, lon: float):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "format": "json",
                "lat": lat,
                "lon": lon
            },
            headers={
                "User-Agent": "Diagnopet/1.0 (diagnopet.com)"
            },
            timeout=10
        )
        return res.json()