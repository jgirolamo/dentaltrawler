"""
FastAPI backend for Dental Clinic Search - Vercel Serverless Version
Adapted to work with Vercel's serverless functions
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# FastAPI app - routes are defined without /api prefix
# Vercel automatically routes /api/* requests to this function
app = FastAPI(title="Dental Clinic API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data file paths - Vercel serverless functions can read from project files
# Files need to be in the same directory or use absolute paths
DATA_DIR = Path(__file__).parent.parent  # Go up from api/ to root
JSON_FILE = DATA_DIR / "dental_clinics_london.json"
METADATA_FILE = DATA_DIR / "metadata.json"

# Fallback: try to load from environment variable (for embedded data)
# Or use relative path from api folder
if not JSON_FILE.exists():
    # Try relative to api folder
    JSON_FILE = Path(__file__).parent / "dental_clinics_london.json"
if not METADATA_FILE.exists():
    METADATA_FILE = Path(__file__).parent / "metadata.json"

# Cache for loaded data (serverless functions can cache in memory)
_data_cache = None
_metadata_cache = None


class ClinicResponse(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    services: List[str] = []
    languages: List[str] = []
    link: Optional[str] = None
    source: Optional[str] = None
    area: Optional[str] = None
    postcode: Optional[str] = None
    nhs: Optional[bool] = None
    private: Optional[bool] = None
    emergency: Optional[bool] = None
    children: Optional[bool] = None
    wheelchair_access: Optional[bool] = None
    parking: Optional[bool] = None
    rating: Optional[float] = None
    opening_hours: Optional[str] = None


class SearchRequest(BaseModel):
    search_text: Optional[str] = None
    area: Optional[str] = None
    postcode: Optional[str] = None
    services: List[str] = []
    languages: List[str] = []
    nhs: Optional[bool] = None
    private: Optional[bool] = None
    emergency: Optional[bool] = None
    children: Optional[bool] = None
    wheelchair: Optional[bool] = None
    parking: Optional[bool] = None
    min_rating: Optional[float] = None
    min_score: Optional[int] = 0
    sort_by: str = "match"
    limit: Optional[int] = None


class MatchResult(BaseModel):
    clinic: ClinicResponse
    match: Dict
    score: int


class StatisticsResponse(BaseModel):
    total_clinics: int
    total_services: int
    total_languages: int
    avg_services_per_clinic: float
    service_counts: Dict[str, int]
    language_counts: Dict[str, int]
    last_updated: Optional[str] = None


def load_clinics() -> List[Dict]:
    """Load clinics from JSON file with caching"""
    global _data_cache
    
    if _data_cache is not None:
        return _data_cache
    
    try:
        # Try multiple paths
        paths_to_try = [
            JSON_FILE,
            Path(__file__).parent.parent / "dental_clinics_london.json",
            Path(__file__).parent / "dental_clinics_london.json",
        ]
        
        for json_path in paths_to_try:
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    _data_cache = json.load(f)
                    logger.info(f"Loaded {len(_data_cache)} clinics from {json_path}")
                    return _data_cache
        
        # Fallback: try environment variable (for embedded data)
        if os.getenv('CLINICS_JSON_DATA'):
            _data_cache = json.loads(os.getenv('CLINICS_JSON_DATA'))
            return _data_cache
        
        logger.warning("No JSON file found, returning empty list")
        return []
    except Exception as e:
        logger.error(f"Error loading clinics: {e}")
        return []


def load_metadata() -> Dict:
    """Load metadata with caching"""
    global _metadata_cache
    
    if _metadata_cache is not None:
        return _metadata_cache
    
    try:
        paths_to_try = [
            METADATA_FILE,
            Path(__file__).parent.parent / "metadata.json",
            Path(__file__).parent / "metadata.json",
        ]
        
        for meta_path in paths_to_try:
            if meta_path.exists():
                with open(meta_path, 'r', encoding='utf-8') as f:
                    _metadata_cache = json.load(f)
                    return _metadata_cache
        
        # Fallback: environment variable
        if os.getenv('METADATA_JSON_DATA'):
            _metadata_cache = json.loads(os.getenv('METADATA_JSON_DATA'))
            return _metadata_cache
        
        return {}
    except Exception as e:
        logger.error(f"Error loading metadata: {e}")
        return {}


def calculate_match_score(clinic: Dict, search_text: Optional[str], 
                         selected_services: List[str], 
                         selected_languages: List[str]) -> Dict:
    """Calculate match score for a clinic"""
    score = 0
    max_score = 100
    match_details = []
    matched_services = []
    matched_languages = []

    # Text search (30 points)
    if search_text:
        text = search_text.lower()
        name_match = text in clinic.get('name', '').lower()
        address_match = text in clinic.get('address', '').lower()
        languages = [l.lower() for l in clinic.get('languages', [])]
        language_match = any(text in lang for lang in languages)
        services = [s.lower() for s in clinic.get('services', [])]
        service_match = any(text in svc for svc in services)
        
        if name_match:
            score += 12
            match_details.append('Name matches')
        if address_match:
            score += 8
            match_details.append('Address matches')
        if language_match:
            score += 5
            match_details.append('Language matches')
        if service_match:
            score += 5
            match_details.append('Service matches')
    else:
        max_score -= 30

    # Services match (40 points)
    if selected_services:
        clinic_services = clinic.get('services', [])
        matched_services = [s for s in selected_services 
                          if any(cs.lower() == s.lower() for cs in clinic_services)]
        service_score = (len(matched_services) / len(selected_services)) * 40
        score += service_score
        
        if matched_services:
            match_details.append(f"{len(matched_services)}/{len(selected_services)} services matched")
    else:
        max_score -= 40

    # Languages match (30 points)
    if selected_languages:
        clinic_languages = clinic.get('languages', [])
        matched_languages = [l for l in selected_languages 
                           if any(cl.lower() == l.lower() for cl in clinic_languages)]
        language_score = (len(matched_languages) / len(selected_languages)) * 30
        score += language_score
        
        if matched_languages:
            match_details.append(f"{len(matched_languages)}/{len(selected_languages)} languages matched")
    else:
        max_score -= 30

    # Normalize score to percentage
    percentage = int((score / max_score) * 100) if max_score > 0 else 100
    
    return {
        "score": percentage,
        "details": match_details,
        "matched_services": matched_services,
        "matched_languages": matched_languages
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Dental Clinic API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/metadata")
async def get_metadata():
    """Get metadata about data freshness"""
    return load_metadata()


@app.get("/clinics")
async def get_clinics(
    limit: Optional[int] = Query(None, description="Limit number of results"),
    offset: Optional[int] = Query(0, description="Offset for pagination")
):
    """Get all clinics with optional pagination"""
    clinics = load_clinics()
    
    if offset:
        clinics = clinics[offset:]
    if limit:
        clinics = clinics[:limit]
    
    return clinics


@app.post("/search")
async def search_clinics(request: SearchRequest):
    """Search clinics with filters and match scoring"""
    clinics = load_clinics()
    
    results = []
    for clinic in clinics:
        # Basic filters
        if request.nhs is not None and clinic.get('nhs') != request.nhs:
            continue
        if request.private is not None and clinic.get('private') != request.private:
            continue
        if request.emergency is not None and clinic.get('emergency') != request.emergency:
            continue
        if request.children is not None and clinic.get('children') != request.children:
            continue
        if request.wheelchair is not None and clinic.get('wheelchair_access') != request.wheelchair:
            continue
        if request.parking is not None and clinic.get('parking') != request.parking:
            continue
        if request.min_rating and (not clinic.get('rating') or clinic.get('rating', 0) < request.min_rating):
            continue
        
        # Area and postcode filters
        if request.area:
            area = clinic.get('area', '').lower()
            address = clinic.get('address', '').lower()
            if request.area.lower() not in area and request.area.lower() not in address:
                continue
        
        if request.postcode:
            postcode = clinic.get('postcode', '').upper()
            address = clinic.get('address', '').upper()
            if request.postcode.upper() not in postcode and request.postcode.upper() not in address:
                continue
        
        # Text search filter
        if request.search_text:
            search_lower = request.search_text.lower()
            name_match = search_lower in clinic.get('name', '').lower()
            address_match = search_lower in clinic.get('address', '').lower()
            languages = [l.lower() for l in clinic.get('languages', [])]
            language_match = any(search_lower in lang for lang in languages)
            services = [s.lower() for s in clinic.get('services', [])]
            service_match = any(search_lower in svc for svc in services)
            
            if not (name_match or address_match or language_match or service_match):
                continue
        
        # Calculate match score
        match = calculate_match_score(
            clinic, 
            request.search_text, 
            request.services, 
            request.languages
        )
        
        if match['score'] < request.min_score:
            continue
        
        results.append({
            "clinic": clinic,
            "match": match,
            "score": match['score']
        })
    
    # Sort results
    if request.sort_by == "match":
        results.sort(key=lambda x: x['score'], reverse=True)
    elif request.sort_by == "name":
        results.sort(key=lambda x: x['clinic'].get('name', ''))
    elif request.sort_by == "services":
        results.sort(key=lambda x: len(x['clinic'].get('services', [])), reverse=True)
    elif request.sort_by == "rating":
        results.sort(key=lambda x: x['clinic'].get('rating', 0), reverse=True)
    
    if request.limit:
        results = results[:request.limit]
    
    return results


@app.get("/statistics")
async def get_statistics():
    """Get statistics about clinics, services, and languages"""
    clinics = load_clinics()
    metadata = load_metadata()
    
    all_services = set()
    all_languages = set()
    total_services_count = 0
    
    service_counts = {}
    language_counts = {}
    
    for clinic in clinics:
        services = clinic.get('services', [])
        languages = clinic.get('languages', [])
        
        for service in services:
            all_services.add(service)
            service_counts[service] = service_counts.get(service, 0) + 1
        
        for language in languages:
            all_languages.add(language)
            language_counts[language] = language_counts.get(language, 0) + 1
        
        total_services_count += len(services)
    
    avg_services = total_services_count / len(clinics) if clinics else 0
    
    return {
        "total_clinics": len(clinics),
        "total_services": len(all_services),
        "total_languages": len(all_languages),
        "avg_services_per_clinic": round(avg_services, 1),
        "service_counts": service_counts,
        "language_counts": language_counts,
        "last_updated": metadata.get('last_updated')
    }


@app.get("/services")
async def get_services():
    """Get all unique services"""
    clinics = load_clinics()
    services = set()
    
    for clinic in clinics:
        services.update(clinic.get('services', []))
    
    return sorted(list(services))


@app.get("/languages")
async def get_languages():
    """Get all unique languages"""
    clinics = load_clinics()
    languages = set()
    
    for clinic in clinics:
        languages.update(clinic.get('languages', []))
    
    return sorted(list(languages))

# Vercel serverless function - export app directly
# Vercel will automatically handle FastAPI apps

