"""
Live Search API for Dental Clinics
Queries real-time data from OpenStreetMap and optional Google Places
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import requests
import json
import time
import os
from datetime import datetime, timedelta
import hashlib

app = FastAPI(title="Dental Clinic Live Search API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory cache
_cache = {}
CACHE_TTL = 300  # 5 minutes

# API Keys (from environment)
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")


class Clinic(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    postcode: Optional[str] = None
    area: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    opening_hours: Optional[str] = None
    source: str = "OpenStreetMap"
    distance_km: Optional[float] = None


class SearchResponse(BaseModel):
    clinics: List[Clinic]
    total: int
    source: str
    cached: bool
    search_time_ms: int


def get_cache_key(query: str, lat: float, lon: float, radius: int) -> str:
    """Generate cache key from search parameters"""
    key_str = f"{query}:{lat:.3f}:{lon:.3f}:{radius}"
    return hashlib.md5(key_str.encode()).hexdigest()


def get_cached(key: str) -> Optional[Dict]:
    """Get from cache if not expired"""
    if key in _cache:
        entry = _cache[key]
        if datetime.now() < entry['expires']:
            return entry['data']
        del _cache[key]
    return None


def set_cache(key: str, data: Dict):
    """Store in cache"""
    _cache[key] = {
        'data': data,
        'expires': datetime.now() + timedelta(seconds=CACHE_TTL)
    }


def search_overpass(lat: float, lon: float, radius_m: int = 5000) -> List[Dict]:
    """
    Search for dentists using OpenStreetMap Overpass API
    Real-time query - always returns fresh data
    """
    # Overpass QL query
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
            headers={'User-Agent': 'DentalTrawler/2.0'},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data.get('elements', [])
    except Exception as e:
        print(f"Overpass API error: {e}")
        return []


def search_google_places(lat: float, lon: float, radius_m: int = 5000) -> List[Dict]:
    """
    Search using Google Places API (requires API key)
    Returns richer data with ratings and reviews
    """
    if not GOOGLE_PLACES_API_KEY:
        return []

    try:
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            'location': f"{lat},{lon}",
            'radius': radius_m,
            'type': 'dentist',
            'key': GOOGLE_PLACES_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('results', [])
    except Exception as e:
        print(f"Google Places API error: {e}")
        return []


def convert_osm_to_clinic(element: Dict, user_lat: float, user_lon: float) -> Optional[Clinic]:
    """Convert OpenStreetMap element to Clinic model"""
    tags = element.get('tags', {})
    name = tags.get('name')

    if not name:
        return None

    lat = element.get('lat')
    lon = element.get('lon')

    # Calculate distance if coordinates available
    distance = None
    if lat and lon:
        from math import radians, sin, cos, sqrt, atan2
        R = 6371  # Earth radius in km

        lat1, lon1 = radians(user_lat), radians(user_lon)
        lat2, lon2 = radians(lat), radians(lon)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = round(R * c, 2)

    # Build address
    address_parts = []
    if tags.get('addr:housenumber'):
        address_parts.append(tags['addr:housenumber'])
    if tags.get('addr:street'):
        address_parts.append(tags['addr:street'])
    if tags.get('addr:city'):
        address_parts.append(tags['addr:city'])
    if tags.get('addr:postcode'):
        address_parts.append(tags['addr:postcode'])

    return Clinic(
        id=f"osm_{element.get('id', '')}",
        name=name,
        address=', '.join(address_parts) if address_parts else None,
        phone=tags.get('phone') or tags.get('contact:phone'),
        website=tags.get('website') or tags.get('contact:website'),
        email=tags.get('email') or tags.get('contact:email'),
        postcode=tags.get('addr:postcode'),
        area=tags.get('addr:city') or tags.get('addr:suburb'),
        lat=lat,
        lon=lon,
        opening_hours=tags.get('opening_hours'),
        source="OpenStreetMap",
        distance_km=distance
    )


def convert_google_to_clinic(place: Dict, user_lat: float, user_lon: float) -> Clinic:
    """Convert Google Places result to Clinic model"""
    location = place.get('geometry', {}).get('location', {})
    lat = location.get('lat')
    lon = location.get('lng')

    # Calculate distance
    distance = None
    if lat and lon:
        from math import radians, sin, cos, sqrt, atan2
        R = 6371

        lat1, lon1 = radians(user_lat), radians(user_lon)
        lat2, lon2 = radians(lat), radians(lon)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = round(R * c, 2)

    return Clinic(
        id=f"google_{place.get('place_id', '')}",
        name=place.get('name', ''),
        address=place.get('vicinity'),
        lat=lat,
        lon=lon,
        rating=place.get('rating'),
        reviews_count=place.get('user_ratings_total'),
        source="Google Places",
        distance_km=distance
    )


# London center coordinates (default)
LONDON_CENTER = (51.5074, -0.1278)

# London area bounding box
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
    'tower-hamlets': (51.5099, -0.0059),
    'greenwich': (51.4892, 0.0648),
    'lewisham': (51.4452, -0.0209),
    'southwark': (51.5035, -0.0804),
    'lambeth': (51.4571, -0.1231),
    'wandsworth': (51.4571, -0.1923),
    'hammersmith': (51.4927, -0.2339),
    'kensington': (51.5000, -0.1916),
    'brent': (51.5673, -0.2711),
    'ealing': (51.5130, -0.3089),
    'hounslow': (51.4746, -0.3680),
    'richmond': (51.4613, -0.3037),
    'kingston': (51.4085, -0.3064),
    'merton': (51.4014, -0.1958),
    'sutton': (51.3618, -0.1945),
    'croydon': (51.3762, -0.0982),
    'bromley': (51.4039, 0.0198),
    'bexley': (51.4549, 0.1505),
    'havering': (51.5779, 0.2120),
    'barking': (51.5362, 0.0798),
    'redbridge': (51.5590, 0.0741),
    'waltham-forest': (51.5886, -0.0117),
    'haringey': (51.5906, -0.1110),
    'enfield': (51.6538, -0.0799),
    'barnet': (51.6252, -0.1517),
    'harrow': (51.5898, -0.3346),
    'hillingdon': (51.5441, -0.4760),
}


@app.get("/")
async def root():
    return {
        "name": "Dental Clinic Live Search API",
        "version": "2.0.0",
        "endpoints": {
            "/search": "Live search for dental clinics",
            "/areas": "List of London areas",
            "/health": "Health check"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/areas")
async def get_areas():
    """Get list of London areas for searching"""
    return {
        "areas": list(LONDON_AREAS.keys()),
        "default": "central"
    }


@app.get("/search", response_model=SearchResponse)
async def search_clinics(
    q: Optional[str] = Query(None, description="Search query (clinic name, area, postcode)"),
    area: Optional[str] = Query(None, description="London area (e.g., 'central', 'hackney')"),
    lat: Optional[float] = Query(None, description="Latitude for location-based search"),
    lon: Optional[float] = Query(None, description="Longitude for location-based search"),
    radius: int = Query(5000, description="Search radius in meters (default 5km)"),
    limit: int = Query(50, description="Maximum results to return"),
    use_google: bool = Query(False, description="Also search Google Places (requires API key)")
):
    """
    Search for dental clinics in real-time

    - If area is provided, searches around that London area
    - If lat/lon provided, searches around those coordinates
    - If q (query) contains a postcode, tries to geocode it
    - Results are sorted by distance from search center
    """
    start_time = time.time()

    # Determine search center
    if lat is not None and lon is not None:
        search_lat, search_lon = lat, lon
    elif area and area.lower() in LONDON_AREAS:
        search_lat, search_lon = LONDON_AREAS[area.lower()]
    else:
        # Default to central London
        search_lat, search_lon = LONDON_CENTER

    # Check cache
    cache_key = get_cache_key(q or '', search_lat, search_lon, radius)
    cached_data = get_cached(cache_key)

    if cached_data:
        return SearchResponse(
            clinics=cached_data['clinics'][:limit],
            total=cached_data['total'],
            source=cached_data['source'],
            cached=True,
            search_time_ms=int((time.time() - start_time) * 1000)
        )

    # Fetch from Overpass API
    osm_elements = search_overpass(search_lat, search_lon, radius)

    clinics = []
    for element in osm_elements:
        if element.get('type') in ('node', 'way') and element.get('tags'):
            clinic = convert_osm_to_clinic(element, search_lat, search_lon)
            if clinic:
                clinics.append(clinic)

    # Optionally add Google Places results
    if use_google and GOOGLE_PLACES_API_KEY:
        google_places = search_google_places(search_lat, search_lon, radius)
        for place in google_places:
            clinic = convert_google_to_clinic(place, search_lat, search_lon)
            clinics.append(clinic)

    # Filter by query if provided
    if q:
        q_lower = q.lower()
        clinics = [
            c for c in clinics
            if q_lower in (c.name or '').lower()
            or q_lower in (c.address or '').lower()
            or q_lower in (c.postcode or '').lower()
            or q_lower in (c.area or '').lower()
        ]

    # Sort by distance
    clinics.sort(key=lambda c: c.distance_km if c.distance_km else 999)

    # Deduplicate by name
    seen = set()
    unique_clinics = []
    for c in clinics:
        name_key = c.name.lower().strip()
        if name_key not in seen:
            seen.add(name_key)
            unique_clinics.append(c)

    # Cache results
    source = "OpenStreetMap" + (" + Google Places" if use_google and GOOGLE_PLACES_API_KEY else "")
    set_cache(cache_key, {
        'clinics': unique_clinics,
        'total': len(unique_clinics),
        'source': source
    })

    return SearchResponse(
        clinics=unique_clinics[:limit],
        total=len(unique_clinics),
        source=source,
        cached=False,
        search_time_ms=int((time.time() - start_time) * 1000)
    )


@app.get("/nearby")
async def nearby_clinics(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius: int = Query(2000, description="Radius in meters"),
    limit: int = Query(20, description="Max results")
):
    """
    Find dental clinics near a specific location
    Useful for "near me" functionality
    """
    return await search_clinics(lat=lat, lon=lon, radius=radius, limit=limit)


# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
