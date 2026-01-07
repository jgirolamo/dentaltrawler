"""
Secure Dental Clinic Search API
- API Key Authentication
- Rate Limiting
- Request Logging
- Proprietary Data (no source attribution)
"""

from fastapi import FastAPI, Query, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Dict, Optional
import requests
import json
import time
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DentalAPI")

app = FastAPI(
    title="Dental Clinic Search API",
    version="2.0.0",
    docs_url=None,  # Disable Swagger UI in production
    redoc_url=None  # Disable ReDoc in production
)

# ==================== SECURITY CONFIG ====================

# API Keys - In production, store in database or secrets manager
API_KEYS = {
    os.getenv("API_KEY_ADMIN", "admin-key-change-me"): {"name": "Admin", "tier": "unlimited"},
    os.getenv("API_KEY_USER", "user-key-change-me"): {"name": "User", "tier": "standard"},
}

# Generate a secure API key for the frontend
FRONTEND_API_KEY = os.getenv("FRONTEND_API_KEY", secrets.token_urlsafe(32))

# Add frontend key to allowed keys
API_KEYS[FRONTEND_API_KEY] = {"name": "Frontend", "tier": "standard"}

# Rate limiting config
RATE_LIMITS = {
    "unlimited": {"requests": 10000, "window": 3600},  # 10k/hour
    "standard": {"requests": 100, "window": 3600},     # 100/hour
    "free": {"requests": 10, "window": 3600},          # 10/hour
}

# CORS - Restrict to your domains in production
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ==================== RATE LIMITING ====================

rate_limit_store = defaultdict(lambda: {"count": 0, "reset_at": datetime.now()})

def check_rate_limit(api_key: str, tier: str) -> bool:
    """Check if request is within rate limit"""
    limits = RATE_LIMITS.get(tier, RATE_LIMITS["free"])
    key_data = rate_limit_store[api_key]

    now = datetime.now()
    if now > key_data["reset_at"]:
        key_data["count"] = 0
        key_data["reset_at"] = now + timedelta(seconds=limits["window"])

    key_data["count"] += 1
    return key_data["count"] <= limits["requests"]

def get_remaining_requests(api_key: str, tier: str) -> int:
    """Get remaining requests for this key"""
    limits = RATE_LIMITS.get(tier, RATE_LIMITS["free"])
    key_data = rate_limit_store[api_key]
    return max(0, limits["requests"] - key_data["count"])

# ==================== AUTHENTICATION ====================

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(request: Request, api_key: str = Depends(api_key_header)):
    """Verify API key and check rate limits"""
    # Log request
    logger.info(f"Request: {request.method} {request.url.path} from {request.client.host}")

    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    if api_key not in API_KEYS:
        logger.warning(f"Invalid API key attempt from {request.client.host}")
        raise HTTPException(status_code=403, detail="Invalid API key")

    key_info = API_KEYS[api_key]
    tier = key_info.get("tier", "free")

    if not check_rate_limit(api_key, tier):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )

    return {"key": api_key, "tier": tier, "name": key_info.get("name")}

# ==================== DATA MODELS ====================

class Clinic(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    postcode: Optional[str] = None
    area: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    rating: Optional[float] = None
    distance_km: Optional[float] = None
    opening_hours: Optional[str] = None
    # Note: No "source" field - proprietary


class SearchResponse(BaseModel):
    clinics: List[Clinic]
    total: int
    search_time_ms: int
    remaining_requests: int

# ==================== CACHE ====================

_cache = {}
CACHE_TTL = 300

def get_cache_key(lat: float, lon: float, radius: int) -> str:
    key_str = f"{lat:.3f}:{lon:.3f}:{radius}"
    return hashlib.md5(key_str.encode()).hexdigest()

def get_cached(key: str) -> Optional[Dict]:
    if key in _cache:
        entry = _cache[key]
        if datetime.now() < entry['expires']:
            return entry['data']
        del _cache[key]
    return None

def set_cache(key: str, data: Dict):
    _cache[key] = {
        'data': data,
        'expires': datetime.now() + timedelta(seconds=CACHE_TTL)
    }

# ==================== DATA FETCHING ====================

def fetch_clinics(lat: float, lon: float, radius_m: int = 5000) -> List[Dict]:
    """Fetch dental clinics - internal method, no source exposed"""
    query = f"""
    [out:json][timeout:30];
    (
      node["amenity"="dentist"](around:{radius_m},{lat},{lon});
      way["amenity"="dentist"](around:{radius_m},{lat},{lon});
      node["healthcare"="dentist"](around:{radius_m},{lat},{lon});
      way["healthcare"="dentist"](around:{radius_m},{lat},{lon});
    );
    out body;
    >;
    out skel qt;
    """

    try:
        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={'data': query},
            headers={'User-Agent': 'DentalSearchAPI/2.0'},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data.get('elements', [])
    except Exception as e:
        logger.error(f"Data fetch error: {e}")
        return []


def convert_to_clinic(element: Dict, user_lat: float, user_lon: float) -> Optional[Clinic]:
    """Convert raw data to proprietary Clinic format"""
    tags = element.get('tags', {})
    name = tags.get('name')

    if not name:
        return None

    lat = element.get('lat')
    lon = element.get('lon')

    # Calculate distance
    distance = None
    if lat and lon:
        from math import radians, sin, cos, sqrt, atan2
        R = 6371
        lat1, lon1 = radians(user_lat), radians(user_lon)
        lat2, lon2 = radians(lat), radians(lon)
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = round(R * c, 2)

    # Build address
    address_parts = []
    for key in ['addr:housenumber', 'addr:street', 'addr:city', 'addr:postcode']:
        if tags.get(key):
            address_parts.append(tags[key])

    # Generate unique ID (proprietary, not exposing OSM ID)
    clinic_id = hashlib.md5(f"{name}{lat}{lon}".encode()).hexdigest()[:12]

    return Clinic(
        id=clinic_id,
        name=name,
        address=', '.join(address_parts) if address_parts else None,
        phone=tags.get('phone') or tags.get('contact:phone'),
        website=tags.get('website') or tags.get('contact:website'),
        postcode=tags.get('addr:postcode'),
        area=tags.get('addr:city') or tags.get('addr:suburb'),
        lat=lat,
        lon=lon,
        opening_hours=tags.get('opening_hours'),
        distance_km=distance
    )

# ==================== LONDON AREAS ====================

LONDON_AREAS = {
    'central': (51.5074, -0.1278),
    'north': (51.5874, -0.1278),
    'south': (51.4274, -0.1278),
    'east': (51.5074, 0.0522),
    'west': (51.5074, -0.3078),
    'city': (51.5155, -0.0922),
    'westminster': (51.4975, -0.1357),
    'camden': (51.5290, -0.1255),
    'islington': (51.5465, -0.1058),
    'hackney': (51.5450, -0.0553),
    'greenwich': (51.4892, 0.0648),
    'southwark': (51.5035, -0.0804),
    'lambeth': (51.4571, -0.1231),
    'kensington': (51.5000, -0.1916),
    'hammersmith': (51.4927, -0.2339),
    'kilburn': (51.5372, -0.1910),
    'hampstead': (51.5565, -0.1781),
    'brixton': (51.4613, -0.1156),
    'shoreditch': (51.5246, -0.0774),
    'stratford': (51.5423, -0.0016),
    'wimbledon': (51.4214, -0.2064),
    'clapham': (51.4620, -0.1380),
    'fulham': (51.4749, -0.2040),
    'putney': (51.4610, -0.2160),
    'ealing': (51.5130, -0.3089),
}

# UK Postcode to coordinates lookup
POSTCODE_COORDS = {
    'nw6': (51.5372, -0.1910),   # Kilburn/West Hampstead
    'nw3': (51.5565, -0.1781),   # Hampstead
    'nw1': (51.5343, -0.1440),   # Camden Town
    'nw8': (51.5320, -0.1720),   # St John's Wood
    'sw1': (51.4975, -0.1357),   # Westminster
    'sw3': (51.4905, -0.1680),   # Chelsea
    'sw6': (51.4749, -0.2040),   # Fulham
    'sw11': (51.4620, -0.1670),  # Battersea
    'se1': (51.5035, -0.0804),   # Southwark
    'e1': (51.5150, -0.0720),    # Whitechapel
    'e2': (51.5290, -0.0560),    # Bethnal Green
    'e8': (51.5450, -0.0553),    # Hackney
    'e14': (51.5070, -0.0235),   # Canary Wharf
    'ec1': (51.5230, -0.1020),   # Clerkenwell
    'ec2': (51.5194, -0.0880),   # City
    'w1': (51.5142, -0.1494),    # West End
    'w2': (51.5130, -0.1800),    # Paddington
    'w8': (51.5000, -0.1916),    # Kensington
    'w11': (51.5090, -0.2050),   # Notting Hill
    'wc1': (51.5230, -0.1200),   # Bloomsbury
    'wc2': (51.5117, -0.1223),   # Covent Garden
    'n1': (51.5465, -0.1058),    # Islington
    'n7': (51.5600, -0.1200),    # Holloway
    'n16': (51.5630, -0.0750),   # Stoke Newington
}

def geocode_postcode(postcode: str) -> Optional[tuple]:
    """Convert UK postcode to coordinates"""
    # Normalize postcode (lowercase, remove spaces)
    pc = postcode.lower().replace(' ', '')

    # Try exact match first
    if pc in POSTCODE_COORDS:
        return POSTCODE_COORDS[pc]

    # Try prefix match (e.g., "nw6 7" -> "nw6")
    for prefix in POSTCODE_COORDS:
        if pc.startswith(prefix):
            return POSTCODE_COORDS[prefix]

    # Try geocoding via Nominatim
    try:
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': f'{postcode}, London, UK', 'format': 'json', 'limit': 1},
            headers={'User-Agent': 'DentalSearchAPI/2.0'},
            timeout=5
        )
        if response.ok and response.json():
            result = response.json()[0]
            return (float(result['lat']), float(result['lon']))
    except:
        pass

    return None

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "name": "Dental Clinic Search API",
        "version": "2.0.0",
        "authentication": "API key required in X-API-Key header"
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/key")
async def get_frontend_key():
    """Get the frontend API key (for initial setup only)"""
    return {
        "key": FRONTEND_API_KEY,
        "note": "Store this securely. This endpoint will be disabled in production."
    }


@app.get("/areas")
async def get_areas(auth: dict = Depends(verify_api_key)):
    """Get list of available London areas"""
    return {"areas": list(LONDON_AREAS.keys())}


@app.get("/search", response_model=SearchResponse)
async def search_clinics(
    request: Request,
    auth: dict = Depends(verify_api_key),
    q: Optional[str] = Query(None, description="Search query or postcode"),
    area: Optional[str] = Query(None, description="London area"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    radius: int = Query(5000, description="Radius in meters"),
    limit: int = Query(50, description="Max results")
):
    """
    Search for dental clinics

    Requires valid API key in X-API-Key header
    Supports postcode search (e.g., NW6, SW1, E14)
    """
    start_time = time.time()

    # Determine search center
    search_lat, search_lon = None, None

    # Check if query looks like a postcode
    if q:
        coords = geocode_postcode(q)
        if coords:
            search_lat, search_lon = coords
            logger.info(f"Geocoded postcode {q} to {coords}")

    # Fall back to explicit lat/lon
    if search_lat is None and lat is not None and lon is not None:
        search_lat, search_lon = lat, lon

    # Fall back to area
    if search_lat is None and area and area.lower() in LONDON_AREAS:
        search_lat, search_lon = LONDON_AREAS[area.lower()]

    # Default to central London
    if search_lat is None:
        search_lat, search_lon = LONDON_AREAS['central']

    # Check cache
    cache_key = get_cache_key(search_lat, search_lon, radius)
    cached_data = get_cached(cache_key)

    if cached_data:
        clinics = cached_data
    else:
        # Fetch fresh data
        elements = fetch_clinics(search_lat, search_lon, radius)
        clinics = []
        for element in elements:
            if element.get('type') in ('node', 'way') and element.get('tags'):
                clinic = convert_to_clinic(element, search_lat, search_lon)
                if clinic:
                    clinics.append(clinic)

        # Cache results
        set_cache(cache_key, clinics)

    # Filter by query
    if q:
        q_lower = q.lower()
        clinics = [
            c for c in clinics
            if q_lower in (c.name or '').lower()
            or q_lower in (c.address or '').lower()
            or q_lower in (c.postcode or '').lower()
        ]

    # Sort by distance
    clinics.sort(key=lambda c: c.distance_km if c.distance_km else 999)

    # Deduplicate
    seen = set()
    unique_clinics = []
    for c in clinics:
        if c.name.lower() not in seen:
            seen.add(c.name.lower())
            unique_clinics.append(c)

    remaining = get_remaining_requests(auth["key"], auth["tier"])

    return SearchResponse(
        clinics=unique_clinics[:limit],
        total=len(unique_clinics),
        search_time_ms=int((time.time() - start_time) * 1000),
        remaining_requests=remaining
    )


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*50)
    print("🔐 SECURE DENTAL CLINIC API")
    print("="*50)
    print(f"\n📋 Frontend API Key: {FRONTEND_API_KEY}")
    print("\n⚠️  Store this key securely!")
    print("    Add to frontend: VITE_API_KEY=<key>")
    print("\n" + "="*50 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
