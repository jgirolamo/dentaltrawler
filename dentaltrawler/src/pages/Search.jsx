import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import './Search.css';

function Search() {
  const [services, setServices] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [metadata, setMetadata] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  
  // Search form state
  const [searchText, setSearchText] = useState('');
  const [areaFilter, setAreaFilter] = useState('');
  const [postcodeFilter, setPostcodeFilter] = useState('');
  const [selectedServices, setSelectedServices] = useState([]);
  const [selectedLanguages, setSelectedLanguages] = useState([]);
  const [sortBy, setSortBy] = useState('match');
  const [minScore, setMinScore] = useState(0);
  const [minRating, setMinRating] = useState(0);
  const [filters, setFilters] = useState({
    nhs: false,
    private: false,
    emergency: false,
    children: false,
    wheelchair: false,
    parking: false
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  async function loadInitialData() {
    try {
      const [servicesData, languagesData, metadataData] = await Promise.all([
        api.getServices().catch(() => []),
        api.getLanguages().catch(() => []),
        api.getMetadata().catch(() => null)
      ]);
      
      setServices(servicesData);
      setLanguages(languagesData);
      setMetadata(metadataData);
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  }

  async function performSearch() {
    setLoading(true);
    try {
      const searchRequest = {
        search_text: searchText || null,
        area: areaFilter || null,
        postcode: postcodeFilter || null,
        services: selectedServices,
        languages: selectedLanguages,
        nhs: filters.nhs || null,
        private: filters.private || null,
        emergency: filters.emergency || null,
        children: filters.children || null,
        wheelchair: filters.wheelchair || null,
        parking: filters.parking || null,
        min_rating: minRating > 0 ? minRating : null,
        min_score: minScore,
        sort_by: sortBy
      };

      const searchResults = await api.searchClinics(searchRequest);
      setResults(searchResults);
    } catch (error) {
      console.error('Search error:', error);
      alert('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function toggleService(service) {
    setSelectedServices(prev => 
      prev.includes(service) 
        ? prev.filter(s => s !== service)
        : [...prev, service]
    );
  }

  function toggleLanguage(language) {
    setSelectedLanguages(prev => 
      prev.includes(language) 
        ? prev.filter(l => l !== language)
        : [...prev, language]
    );
  }

  function clearFilters() {
    setSearchText('');
    setAreaFilter('');
    setPostcodeFilter('');
    setSelectedServices([]);
    setSelectedLanguages([]);
    setFilters({
      nhs: false,
      private: false,
      emergency: false,
      children: false,
      wheelchair: false,
      parking: false
    });
    setMinScore(0);
    setMinRating(0);
    setSortBy('match');
  }

  function getScoreClass(score) {
    if (score >= 70) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
  }

  const hasActiveFilters = searchText || areaFilter || postcodeFilter || 
    selectedServices.length > 0 || selectedLanguages.length > 0 ||
    Object.values(filters).some(v => v) || minScore > 0 || minRating > 0;

  return (
    <div className="search-page">
      <div className="container">
        <div className="header">
          <h1>🔍 Dental Clinic Search</h1>
          <p>Find the perfect dental clinic in London based on services and languages</p>
          {metadata?.last_updated && (
            <small>Last updated: {new Date(metadata.last_updated).toLocaleString()}</small>
          )}
          <div className="header-actions">
            <Link to="/dashboard" className="dashboard-link">
              📊 View Dashboard
            </Link>
          </div>
        </div>

        <div className="search-section">
          <div className="quick-search">
            <div className="search-bar">
              <input
                type="text"
                className="main-search-input"
                placeholder="Search by clinic name, address, or language (e.g., Spanish, Polish)..."
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && performSearch()}
              />
              <button
                className="search-button-primary"
                onClick={performSearch}
                disabled={loading}
              >
                {loading ? '⏳ Searching...' : '🔍 Search'}
              </button>
            </div>
            
            <div className="quick-filters">
              <input
                type="text"
                className="quick-filter-input"
                placeholder="Area (e.g., Westminster)"
                value={areaFilter}
                onChange={(e) => setAreaFilter(e.target.value)}
              />
              <input
                type="text"
                className="quick-filter-input"
                placeholder="Postcode (e.g., W1)"
                value={postcodeFilter}
                onChange={(e) => setPostcodeFilter(e.target.value)}
              />
              <button
                className="toggle-filters-btn"
                onClick={() => setShowFilters(!showFilters)}
              >
                {showFilters ? '▲ Hide' : '▼ Advanced'} Filters
              </button>
            </div>
          </div>

          {showFilters && (
            <div className="advanced-filters">
              <div className="filters-grid">
                <div className="filter-column">
                  <h3>Sort & Filter</h3>
                  <div className="filter-controls">
                    <div className="control-group">
                      <label>Sort By</label>
                      <select
                        className="filter-select"
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                      >
                        <option value="match">Match Score</option>
                        <option value="name">Name (A-Z)</option>
                        <option value="services">Most Services</option>
                        <option value="rating">Highest Rating</option>
                      </select>
                    </div>
                    <div className="control-group">
                      <label>Min Match Score</label>
                      <select
                        className="filter-select"
                        value={minScore}
                        onChange={(e) => setMinScore(parseInt(e.target.value))}
                      >
                        <option value="0">Any</option>
                        <option value="30">30%+</option>
                        <option value="50">50%+</option>
                        <option value="70">70%+</option>
                        <option value="90">90%+</option>
                      </select>
                    </div>
                    <div className="control-group">
                      <label>Min Rating</label>
                      <select
                        className="filter-select"
                        value={minRating}
                        onChange={(e) => setMinRating(parseFloat(e.target.value))}
                      >
                        <option value="0">Any</option>
                        <option value="3">3.0+</option>
                        <option value="3.5">3.5+</option>
                        <option value="4">4.0+</option>
                        <option value="4.5">4.5+</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="filter-column">
                  <h3>Clinic Features</h3>
                  <div className="feature-checkboxes">
                    <label className="feature-checkbox">
                      <input
                        type="checkbox"
                        checked={filters.nhs}
                        onChange={(e) => setFilters({...filters, nhs: e.target.checked})}
                      />
                      <span>NHS Accepting</span>
                    </label>
                    <label className="feature-checkbox">
                      <input
                        type="checkbox"
                        checked={filters.private}
                        onChange={(e) => setFilters({...filters, private: e.target.checked})}
                      />
                      <span>Private</span>
                    </label>
                    <label className="feature-checkbox">
                      <input
                        type="checkbox"
                        checked={filters.emergency}
                        onChange={(e) => setFilters({...filters, emergency: e.target.checked})}
                      />
                      <span>Emergency</span>
                    </label>
                    <label className="feature-checkbox">
                      <input
                        type="checkbox"
                        checked={filters.children}
                        onChange={(e) => setFilters({...filters, children: e.target.checked})}
                      />
                      <span>Children/Pediatric</span>
                    </label>
                    <label className="feature-checkbox">
                      <input
                        type="checkbox"
                        checked={filters.wheelchair}
                        onChange={(e) => setFilters({...filters, wheelchair: e.target.checked})}
                      />
                      <span>Wheelchair Access</span>
                    </label>
                    <label className="feature-checkbox">
                      <input
                        type="checkbox"
                        checked={filters.parking}
                        onChange={(e) => setFilters({...filters, parking: e.target.checked})}
                      />
                      <span>Parking</span>
                    </label>
                  </div>
                </div>
              </div>

              <div className="services-languages-filters">
                <div className="filter-panel">
                  <h3>Services Required</h3>
                  <div className="filter-tags">
                    {services.slice(0, 20).map(service => (
                      <button
                        key={service}
                        className={`filter-tag ${selectedServices.includes(service) ? 'active' : ''}`}
                        onClick={() => toggleService(service)}
                      >
                        {service}
                      </button>
                    ))}
                    {services.length > 20 && (
                      <span className="more-indicator">+{services.length - 20} more</span>
                    )}
                  </div>
                </div>

                <div className="filter-panel">
                  <h3>Languages Spoken</h3>
                  <div className="filter-tags">
                    {languages.map(language => (
                      <button
                        key={language}
                        className={`filter-tag language-tag ${selectedLanguages.includes(language) ? 'active' : ''}`}
                        onClick={() => toggleLanguage(language)}
                      >
                        {language}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {hasActiveFilters && (
                <button className="clear-filters-btn" onClick={clearFilters}>
                  ✕ Clear All Filters
                </button>
              )}
            </div>
          )}
        </div>

        {results.length > 0 && (
          <div className="results-section">
            <div className="results-header">
              <h2>Search Results</h2>
              <div className="results-count">
                {results.length} clinic{results.length !== 1 ? 's' : ''} found
              </div>
            </div>
            <div className="results-container">
              {results.map((result, index) => {
                const { clinic, match } = result;
                const scoreClass = getScoreClass(match.score);
                
                const features = [];
                if (clinic.nhs) features.push('NHS');
                if (clinic.private) features.push('Private');
                if (clinic.emergency) features.push('Emergency');
                if (clinic.children) features.push('Children');
                if (clinic.wheelchair_access) features.push('♿');
                if (clinic.parking) features.push('P');

                return (
                  <div key={index} className="clinic-card">
                    <div className={`match-badge ${scoreClass}`}>
                      {match.score}% Match
                    </div>
                    <div className="clinic-card-header">
                      <div>
                        <h3 className="clinic-name">{clinic.name || 'Unknown Clinic'}</h3>
                        {clinic.rating && (
                          <div className="clinic-rating">
                            ⭐ {clinic.rating}/5.0
                          </div>
                        )}
                      </div>
                      {features.length > 0 && (
                        <div className="clinic-features">
                          {features.map(f => (
                            <span key={f} className="feature-icon">{f}</span>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <div className="clinic-details">
                      {clinic.address && (
                        <div className="detail-item">
                          <span className="detail-icon">📍</span>
                          <span>{clinic.address}</span>
                        </div>
                      )}
                      {clinic.phone && (
                        <div className="detail-item">
                          <span className="detail-icon">📞</span>
                          <span>{clinic.phone}</span>
                        </div>
                      )}
                      {clinic.opening_hours && (
                        <div className="detail-item">
                          <span className="detail-icon">🕐</span>
                          <span>{clinic.opening_hours}</span>
                        </div>
                      )}
                      {clinic.link && (
                        <div className="detail-item">
                          <span className="detail-icon">🌐</span>
                          <a href={clinic.link} target="_blank" rel="noopener noreferrer">
                            Visit Website
                          </a>
                        </div>
                      )}
                    </div>

                    {match.details && match.details.length > 0 && (
                      <div className="match-info">
                        {match.details.join(' • ')}
                      </div>
                    )}

                    <div className="clinic-tags">
                      <div className="tags-section">
                        <strong>Services:</strong>
                        <div className="tags-list">
                          {clinic.services && clinic.services.length > 0 ? (
                            clinic.services.map(s => {
                              const isMatched = match.matched_services?.some(ms => ms.toLowerCase() === s.toLowerCase());
                              return (
                                <span key={s} className={`tag service-tag ${isMatched ? 'matched' : ''}`}>
                                  {s}
                                </span>
                              );
                            })
                          ) : (
                            <span className="no-data">None listed</span>
                          )}
                        </div>
                      </div>
                      <div className="tags-section">
                        <strong>Languages:</strong>
                        <div className="tags-list">
                          {clinic.languages && clinic.languages.length > 0 ? (
                            clinic.languages.map(l => {
                              const isMatched = match.matched_languages?.some(ml => ml.toLowerCase() === l.toLowerCase());
                              return (
                                <span key={l} className={`tag language-tag ${isMatched ? 'matched' : ''}`}>
                                  {l}
                                </span>
                              );
                            })
                          ) : (
                            <span className="no-data">None listed</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {results.length === 0 && !loading && (
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <h3>No results yet</h3>
            <p>Use the search form above to find dental clinics in London</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Search;
