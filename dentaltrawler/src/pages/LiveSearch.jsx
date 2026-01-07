import { useState, useEffect } from 'react';
import { searchClinics, getUserLocation, getAreas } from '../services/api';
import './Search.css';

/**
 * Live Search Page - Real-time dental clinic search
 * Fetches data from OpenStreetMap API
 */
function LiveSearch() {
  // Search state
  const [query, setQuery] = useState('');
  const [area, setArea] = useState('central');
  const [radius, setRadius] = useState(5000);
  const [areas, setAreas] = useState([]);

  // Results state
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchInfo, setSearchInfo] = useState(null);

  // Location state
  const [userLocation, setUserLocation] = useState(null);
  const [useMyLocation, setUseMyLocation] = useState(false);
  const [locationError, setLocationError] = useState(null);

  // Load available areas on mount
  useEffect(() => {
    getAreas()
      .then(data => setAreas(data.areas || []))
      .catch(err => console.error('Failed to load areas:', err));

    // Do initial search
    handleSearch();
  }, []);

  // Get user location
  const handleGetLocation = async () => {
    setLocationError(null);
    try {
      const location = await getUserLocation();
      setUserLocation(location);
      setUseMyLocation(true);
      // Auto-search with new location
      doSearch({ lat: location.lat, lon: location.lon });
    } catch (err) {
      setLocationError('Could not get your location. Please allow location access.');
      console.error('Location error:', err);
    }
  };

  // Perform search
  const doSearch = async (overrides = {}) => {
    setLoading(true);
    setError(null);

    try {
      const params = {
        query: query || undefined,
        area: useMyLocation ? undefined : area,
        lat: useMyLocation && userLocation ? userLocation.lat : undefined,
        lon: useMyLocation && userLocation ? userLocation.lon : undefined,
        radius,
        limit: 100,
        ...overrides
      };

      const data = await searchClinics(params);

      setResults(data.clinics || []);
      setSearchInfo({
        total: data.total,
        source: data.source,
        cached: data.cached,
        searchTime: data.search_time_ms
      });
    } catch (err) {
      setError('Search failed. Make sure the API server is running.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    if (e) e.preventDefault();
    doSearch();
  };

  // Format distance
  const formatDistance = (km) => {
    if (!km) return null;
    if (km < 1) return `${Math.round(km * 1000)}m`;
    return `${km.toFixed(1)}km`;
  };

  return (
    <div className="search-page">
      <header className="search-header">
        <h1>🦷 Find a Dentist</h1>
        <p>Real-time search powered by OpenStreetMap</p>
      </header>

      {/* Search Form */}
      <form className="search-form" onSubmit={handleSearch}>
        <div className="search-row">
          <input
            type="text"
            placeholder="Search by name, postcode, or area..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="search-button" disabled={loading}>
            {loading ? '🔄 Searching...' : '🔍 Search'}
          </button>
        </div>

        <div className="search-options">
          {/* Area selector */}
          <div className="option-group">
            <label>
              <input
                type="radio"
                checked={!useMyLocation}
                onChange={() => setUseMyLocation(false)}
              />
              Search by area:
            </label>
            <select
              value={area}
              onChange={(e) => setArea(e.target.value)}
              disabled={useMyLocation}
            >
              {areas.map(a => (
                <option key={a} value={a}>
                  {a.charAt(0).toUpperCase() + a.slice(1).replace('-', ' ')}
                </option>
              ))}
            </select>
          </div>

          {/* My location */}
          <div className="option-group">
            <label>
              <input
                type="radio"
                checked={useMyLocation}
                onChange={() => {
                  if (!userLocation) {
                    handleGetLocation();
                  } else {
                    setUseMyLocation(true);
                  }
                }}
              />
              Near me
            </label>
            {useMyLocation && userLocation && (
              <span className="location-info">
                📍 Using your location
              </span>
            )}
            {locationError && (
              <span className="location-error">{locationError}</span>
            )}
          </div>

          {/* Radius */}
          <div className="option-group">
            <label>Radius:</label>
            <select
              value={radius}
              onChange={(e) => setRadius(Number(e.target.value))}
            >
              <option value={1000}>1 km</option>
              <option value={2000}>2 km</option>
              <option value={5000}>5 km</option>
              <option value={10000}>10 km</option>
              <option value={20000}>20 km</option>
            </select>
          </div>
        </div>
      </form>

      {/* Error message */}
      {error && (
        <div className="error-message">
          <p>⚠️ {error}</p>
          <p className="error-hint">
            Run the API server: <code>cd api && python3 live_search.py</code>
          </p>
        </div>
      )}

      {/* Search info */}
      {searchInfo && !error && (
        <div className="search-info">
          <span>Found <strong>{searchInfo.total}</strong> clinics</span>
          <span>Source: {searchInfo.source}</span>
          <span>{searchInfo.cached ? '(cached)' : `(${searchInfo.searchTime}ms)`}</span>
        </div>
      )}

      {/* Results */}
      <div className="results-container">
        {loading && (
          <div className="loading">
            <div className="loading-spinner"></div>
            <p>Searching dental clinics...</p>
          </div>
        )}

        {!loading && results.length === 0 && !error && (
          <div className="no-results">
            <p>No clinics found. Try a different area or larger radius.</p>
          </div>
        )}

        {!loading && results.length > 0 && (
          <div className="results-grid">
            {results.map((clinic, index) => (
              <div key={clinic.id || index} className="clinic-card">
                <div className="clinic-header">
                  <h3 className="clinic-name">{clinic.name}</h3>
                  {clinic.distance_km && (
                    <span className="clinic-distance">
                      📍 {formatDistance(clinic.distance_km)}
                    </span>
                  )}
                </div>

                <div className="clinic-details">
                  {clinic.address && (
                    <p className="clinic-address">
                      📍 {clinic.address}
                    </p>
                  )}
                  {clinic.phone && (
                    <p className="clinic-phone">
                      📞 <a href={`tel:${clinic.phone}`}>{clinic.phone}</a>
                    </p>
                  )}
                  {clinic.website && (
                    <p className="clinic-website">
                      🌐 <a href={clinic.website} target="_blank" rel="noopener noreferrer">
                        Website
                      </a>
                    </p>
                  )}
                  {clinic.opening_hours && (
                    <p className="clinic-hours">
                      🕐 {clinic.opening_hours}
                    </p>
                  )}
                  {clinic.rating && (
                    <p className="clinic-rating">
                      ⭐ {clinic.rating} ({clinic.reviews_count} reviews)
                    </p>
                  )}
                </div>

                <div className="clinic-actions">
                  {clinic.phone && (
                    <a href={`tel:${clinic.phone}`} className="action-button">
                      📞 Call
                    </a>
                  )}
                  {clinic.lat && clinic.lon && (
                    <a
                      href={`https://www.google.com/maps/search/?api=1&query=${clinic.lat},${clinic.lon}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="action-button"
                    >
                      🗺️ Directions
                    </a>
                  )}
                </div>

                <div className="clinic-source">
                  Source: {clinic.source}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default LiveSearch;
