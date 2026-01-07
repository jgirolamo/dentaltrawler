/**
 * Secure Dental Clinic Search API Service
 * Authenticated API access with rate limiting
 */

// API configuration
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY || '';

// Default headers with authentication
const getHeaders = () => ({
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY,
});

/**
 * Search for dental clinics in real-time
 * @param {Object} params - Search parameters
 * @param {string} params.query - Text search query
 * @param {string} params.area - London area (e.g., 'hackney', 'central')
 * @param {number} params.lat - Latitude for location search
 * @param {number} params.lon - Longitude for location search
 * @param {number} params.radius - Search radius in meters (default 5000)
 * @param {number} params.limit - Max results (default 50)
 * @returns {Promise<Object>} Search results
 */
export async function searchClinics({
  query = '',
  area = '',
  lat = null,
  lon = null,
  radius = 5000,
  limit = 50
}) {
  const params = new URLSearchParams();

  if (query) params.append('q', query);
  if (area) params.append('area', area);
  if (lat !== null) params.append('lat', lat);
  if (lon !== null) params.append('lon', lon);
  params.append('radius', radius);
  params.append('limit', limit);

  try {
    const response = await fetch(`${API_BASE}/search?${params}`, {
      headers: getHeaders()
    });
    if (!response.ok) {
      if (response.status === 401) throw new Error('API key required');
      if (response.status === 403) throw new Error('Invalid API key');
      if (response.status === 429) throw new Error('Rate limit exceeded');
      throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Search API error:', error);
    throw error;
  }
}

/**
 * Find clinics near the user's location
 * @param {number} lat - User's latitude
 * @param {number} lon - User's longitude
 * @param {number} radius - Search radius in meters
 * @param {number} limit - Max results
 * @returns {Promise<Object>} Nearby clinics
 */
export async function findNearbyClinics(lat, lon, radius = 2000, limit = 20) {
  const params = new URLSearchParams({
    lat,
    lon,
    radius,
    limit
  });

  try {
    const response = await fetch(`${API_BASE}/nearby?${params}`, {
      headers: getHeaders()
    });
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Nearby API error:', error);
    throw error;
  }
}

/**
 * Get list of available London areas
 * @returns {Promise<Object>} Areas list
 */
export async function getAreas() {
  try {
    const response = await fetch(`${API_BASE}/areas`, {
      headers: getHeaders()
    });
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Areas API error:', error);
    throw error;
  }
}

/**
 * Get user's current location
 * @returns {Promise<{lat: number, lon: number}>} User coordinates
 */
export function getUserLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation not supported'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          lat: position.coords.latitude,
          lon: position.coords.longitude
        });
      },
      (error) => {
        reject(error);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // Cache for 5 minutes
      }
    );
  });
}

/**
 * Health check for API
 * @returns {Promise<boolean>} API is healthy
 */
export async function checkApiHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

export default {
  searchClinics,
  findNearbyClinics,
  getAreas,
  getUserLocation,
  checkApiHealth
};
