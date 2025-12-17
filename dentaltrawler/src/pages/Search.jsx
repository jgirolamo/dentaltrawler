<<<<<<< HEAD
import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { clinicsData } from '../clinics';
import './Search.css';

function Search() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(50);
  const MAX_RESULTS = 300;
  
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

  // Extract unique services and languages from embedded data
  const { services, languages } = useMemo(() => {
    const allServices = new Set();
    const allLanguages = new Set();
    
    clinicsData.forEach(clinic => {
      (clinic.services || []).forEach(s => allServices.add(s));
      (clinic.languages || []).forEach(l => allLanguages.add(l));
    });
    
    return {
      services: Array.from(allServices).sort(),
      languages: Array.from(allLanguages).sort()
    };
  }, []);

  // Load all clinics on initial page load
  useEffect(() => {
    // Show all clinics initially (no filters)
    const initialResults = clinicsData.map(clinic => {
      const match = calculateMatchScore(clinic, null, [], []);
      return {
        clinic: clinic,
        match: match,
        score: match.score
      };
    });
    
    // Sort by name initially
    initialResults.sort((a, b) => (a.clinic.name || '').localeCompare(b.clinic.name || ''));
    
    // Limit to MAX_RESULTS
    setResults(initialResults.slice(0, MAX_RESULTS));
  }, []);

  // Calculate match score (same logic as backend)
  function calculateMatchScore(clinic, searchText, selectedServices, selectedLanguages) {
    let score = 0;
    let maxScore = 100;
    const matchDetails = [];
    const matchedServices = [];
    const matchedLanguages = [];

    // Text search (30 points)
    if (searchText) {
      const text = searchText.toLowerCase();
      const nameMatch = (clinic.name || '').toLowerCase().includes(text);
      const addressMatch = (clinic.address || '').toLowerCase().includes(text);
      const languages = (clinic.languages || []).map(l => l.toLowerCase());
      const languageMatch = languages.some(lang => lang.includes(text));
      const services = (clinic.services || []).map(s => s.toLowerCase());
      const serviceMatch = services.some(svc => svc.includes(text));
      
      if (nameMatch) {
        score += 12;
        matchDetails.push('Name matches');
      }
      if (addressMatch) {
        score += 8;
        matchDetails.push('Address matches');
      }
      if (languageMatch) {
        score += 5;
        matchDetails.push('Language matches');
      }
      if (serviceMatch) {
        score += 5;
        matchDetails.push('Service matches');
      }
    } else {
      maxScore -= 30;
    }

    // Services match (40 points)
    if (selectedServices.length > 0) {
      const clinicServices = (clinic.services || []).map(s => s.toLowerCase());
      selectedServices.forEach(s => {
        if (clinicServices.some(cs => cs === s.toLowerCase())) {
          matchedServices.push(s);
        }
      });
      const serviceScore = (matchedServices.length / selectedServices.length) * 40;
      score += serviceScore;
      
      if (matchedServices.length > 0) {
        matchDetails.push(`${matchedServices.length}/${selectedServices.length} services matched`);
      }
    } else {
      maxScore -= 40;
    }

    // Languages match (30 points)
    if (selectedLanguages.length > 0) {
      const clinicLanguages = (clinic.languages || []).map(l => l.toLowerCase());
      selectedLanguages.forEach(l => {
        if (clinicLanguages.some(cl => cl === l.toLowerCase())) {
          matchedLanguages.push(l);
        }
      });
      const languageScore = (matchedLanguages.length / selectedLanguages.length) * 30;
      score += languageScore;
      
      if (matchedLanguages.length > 0) {
        matchDetails.push(`${matchedLanguages.length}/${selectedLanguages.length} languages matched`);
      }
    } else {
      maxScore -= 30;
    }

    // Normalize score to percentage
    const percentage = maxScore > 0 ? Math.round((score / maxScore) * 100) : 100;
    
    return {
      score: percentage,
      details: matchDetails,
      matched_services: matchedServices,
      matched_languages: matchedLanguages
    };
  }

  function performSearch() {
    setLoading(true);
    setCurrentPage(1); // Reset to first page on new search
    
    // Use setTimeout to allow UI to update
    setTimeout(() => {
      const searchResults = [];
      
      for (const clinic of clinicsData) {
        // Basic filters
        if (filters.nhs && !clinic.nhs) continue;
        if (filters.private && !clinic.private) continue;
        if (filters.emergency && !clinic.emergency) continue;
        if (filters.children && !clinic.children) continue;
        if (filters.wheelchair && !clinic.wheelchair_access) continue;
        if (filters.parking && !clinic.parking) continue;
        if (minRating > 0 && (!clinic.rating || clinic.rating < minRating)) continue;
        
        // Area and postcode filters
        if (areaFilter) {
          const area = (clinic.area || '').toLowerCase();
          const address = (clinic.address || '').toLowerCase();
          if (!area.includes(areaFilter.toLowerCase()) && !address.includes(areaFilter.toLowerCase())) {
            continue;
          }
        }
        
        if (postcodeFilter) {
          const postcode = (clinic.postcode || '').toUpperCase();
          const address = (clinic.address || '').toUpperCase();
          if (!postcode.includes(postcodeFilter.toUpperCase()) && !address.includes(postcodeFilter.toUpperCase())) {
            continue;
          }
        }
        
        // Text search filter
        if (searchText) {
          const searchLower = searchText.toLowerCase();
          const nameMatch = (clinic.name || '').toLowerCase().includes(searchLower);
          const addressMatch = (clinic.address || '').toLowerCase().includes(searchLower);
          const languages = (clinic.languages || []).map(l => l.toLowerCase());
          const languageMatch = languages.some(lang => lang.includes(searchLower));
          const services = (clinic.services || []).map(s => s.toLowerCase());
          const serviceMatch = services.some(svc => svc.includes(searchLower));
          
          if (!(nameMatch || addressMatch || languageMatch || serviceMatch)) {
            continue;
          }
        }
        
        // Calculate match score
        const match = calculateMatchScore(clinic, searchText, selectedServices, selectedLanguages);
        
        if (match.score < minScore) {
          continue;
        }
        
        searchResults.push({
          clinic: clinic,
          match: match,
          score: match.score
        });
      }
      
      // Sort results
      if (sortBy === "match") {
        searchResults.sort((a, b) => b.score - a.score);
      } else if (sortBy === "name") {
        searchResults.sort((a, b) => (a.clinic.name || '').localeCompare(b.clinic.name || ''));
      } else if (sortBy === "services") {
        searchResults.sort((a, b) => (b.clinic.services || []).length - (a.clinic.services || []).length);
      } else if (sortBy === "rating") {
        searchResults.sort((a, b) => (b.clinic.rating || 0) - (a.clinic.rating || 0));
      }
      
      // Limit results
      const limitedResults = searchResults.slice(0, MAX_RESULTS);
      setResults(limitedResults);
      setLoading(false);
    }, 10);
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

  // Load all clinics on initial page load
  useEffect(() => {
    // Show all clinics initially (no filters)
    const initialResults = clinicsData.map(clinic => {
      const match = calculateMatchScore(clinic, null, [], []);
      return {
        clinic: clinic,
        match: match,
        score: match.score
      };
    });
    
    // Sort by name initially
    initialResults.sort((a, b) => (a.clinic.name || '').localeCompare(b.clinic.name || ''));
    
    // Limit to MAX_RESULTS
    setResults(initialResults.slice(0, MAX_RESULTS));
  }, []);

  // Pagination calculations
  const totalResults = results.length;
  const totalPages = Math.ceil(totalResults / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentResults = results.slice(startIndex, endIndex);

  function handlePageChange(page) {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function handleItemsPerPageChange(newItemsPerPage) {
    setItemsPerPage(newItemsPerPage);
    setCurrentPage(1); // Reset to first page when changing items per page
  }

  function getPageNumbers() {
    const pages = [];
    const maxVisible = 7;
    
    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 5; i++) pages.push(i);
        pages.push('ellipsis');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1);
        pages.push('ellipsis');
        for (let i = totalPages - 4; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push('ellipsis');
        for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i);
        pages.push('ellipsis');
        pages.push(totalPages);
      }
    }
    return pages;
  }

  return (
    <div className="search-page">
      <div className="container">
        <div className="header">
          <h1>🔍 Private Dental Clinic Search</h1>
          <p>Find the perfect dental clinic in London based on services and languages</p>
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
                placeholder="Search by name, address, language, or service (e.g., Spanish, Orthodontics)..."
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
              <div className="results-stats">
                <div className="results-count">
                  Showing {startIndex + 1}-{Math.min(endIndex, totalResults)} of {totalResults} 
                  {totalResults >= MAX_RESULTS && ` (limited to ${MAX_RESULTS} max)`} clinic{totalResults !== 1 ? 's' : ''} found
                </div>
                <div className="results-controls">
                  <div className="items-per-page-selector">
                    <label htmlFor="itemsPerPage">Show:</label>
                    <select
                      id="itemsPerPage"
                      value={itemsPerPage}
                      onChange={(e) => handleItemsPerPageChange(Number(e.target.value))}
                      className="items-per-page-select"
                    >
                      <option value={25}>25</option>
                      <option value={50}>50</option>
                      <option value={100}>100</option>
                    </select>
                    <span>per page</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="results-container">
              {currentResults.map((result, index) => {
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
            
            {totalPages > 1 && (
              <div className="pagination">
                <button
                  className="pagination-button"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  ← Previous
                </button>
                
                <div className="pagination-pages">
                  {getPageNumbers().map((page, idx) => {
                    if (page === 'ellipsis') {
                      return <span key={`ellipsis-${idx}`} className="pagination-ellipsis">...</span>;
                    }
                    return (
                      <button
                        key={page}
                        className={`pagination-page ${currentPage === page ? 'active' : ''}`}
                        onClick={() => handlePageChange(page)}
                      >
                        {page}
                      </button>
                    );
                  })}
                </div>
                
                <button
                  className="pagination-button"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  Next →
                </button>
              </div>
            )}
            
            {totalResults >= MAX_RESULTS && (
              <div className="results-limit-notice">
                <small>⚠️ Results limited to {MAX_RESULTS} clinics. Refine your search for more specific results.</small>
              </div>
            )}
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
=======
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { clinicsData } from '../clinics';
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
    emergency: false,
    children: false,
    wheelchair: false,
    parking: false
  });
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(50);
  const MAX_RESULTS = 300;

  useEffect(() => {
    // Try to fetch real data first, fallback to embedded data
    async function loadData() {
      try {
        // Check if clinicsData is loaded
        if (!clinicsData || !Array.isArray(clinicsData) || clinicsData.length === 0) {
          console.error('❌ clinicsData is not loaded or empty');
          setResults([]);
          return;
        }
        
        console.log(`✅ Loaded ${clinicsData.length} clinics`);
        
        // Try fetching real NHS data (if available)
        // const realClinics = await fetchRealClinics();
        // if (realClinics.length > 0) {
        //   clinicsData = realClinics;
        // }
      } catch (error) {
        console.error('❌ Error loading clinic data:', error);
        setResults([]);
        return;
      }
      
      try {
        // Extract unique services and languages from data
        const allServices = new Set();
        const allLanguages = new Set();
        
        clinicsData.forEach(clinic => {
          if (clinic.services && Array.isArray(clinic.services)) {
            clinic.services.forEach(s => allServices.add(s));
          }
          if (clinic.languages && Array.isArray(clinic.languages)) {
            clinic.languages.forEach(l => allLanguages.add(l));
          }
        });
        
        setServices(Array.from(allServices).sort());
        setLanguages(Array.from(allLanguages).sort());
        setMetadata({ last_updated: new Date().toISOString(), total_clinics: clinicsData.length });
        
        // Auto-search on initial load to show all clinics
        const initialResults = clinicsData.map(clinic => ({
          clinic,
          match: { score: 100, details: [], matched_services: [], matched_languages: [] },
          score: 100
        }));
        
        // Limit to MAX_RESULTS for initial display
        const limitedInitialResults = initialResults.slice(0, MAX_RESULTS);
        console.log(`📊 Setting results: ${limitedInitialResults.length} clinics`);
        console.log(`📊 First result:`, limitedInitialResults[0]);
        setResults(limitedInitialResults);
        
        console.log(`✅ Initial results set: ${limitedInitialResults.length} clinics`);
      } catch (error) {
        console.error('❌ Error processing clinic data:', error);
        setResults([]);
      }
    }
    
    loadData();
  }, []);

  function calculateMatchScore(clinic, searchText, selectedServices, selectedLanguages) {
    let score = 0;
    const maxScore = 100;

    // Text search (30 points)
    if (searchText) {
      const text = searchText.toLowerCase();
      if (clinic.name?.toLowerCase().includes(text)) score += 12;
      if (clinic.address?.toLowerCase().includes(text)) score += 8;
      if (clinic.languages?.some(l => l.toLowerCase().includes(text))) score += 5;
      if (clinic.services?.some(s => s.toLowerCase().includes(text))) score += 5;
    }

    // Services match (40 points)
    if (selectedServices.length > 0) {
      const matched = selectedServices.filter(s => 
        clinic.services?.some(cs => cs.toLowerCase() === s.toLowerCase())
      );
      score += (matched.length / selectedServices.length) * 40;
    }

    // Languages match (30 points)
    if (selectedLanguages.length > 0) {
      const matched = selectedLanguages.filter(l => 
        clinic.languages?.some(cl => cl.toLowerCase() === l.toLowerCase())
      );
      score += (matched.length / selectedLanguages.length) * 30;
    }

    return Math.round((score / maxScore) * 100);
  }

  function performSearch() {
    setLoading(true);
    setTimeout(() => {
      try {
        // Validate clinicsData
        if (!clinicsData || !Array.isArray(clinicsData) || clinicsData.length === 0) {
          console.error('❌ clinicsData is not available for search');
          setResults([]);
          setLoading(false);
          return;
        }
        
        const results = [];
        
        for (const clinic of clinicsData) {
          // Apply filters
          if (filters.emergency && !clinic.emergency) continue;
          if (filters.children && !clinic.children) continue;
          if (filters.wheelchair && !clinic.wheelchair_access) continue;
          if (filters.parking && !clinic.parking) continue;
          if (minRating > 0 && (!clinic.rating || clinic.rating < minRating)) continue;
          
          if (areaFilter && !clinic.area?.toLowerCase().includes(areaFilter.toLowerCase()) && 
              !clinic.address?.toLowerCase().includes(areaFilter.toLowerCase())) continue;
          
          if (postcodeFilter) {
            const filterUpper = postcodeFilter.toUpperCase().trim();
            const clinicPostcode = (clinic.postcode || '').toUpperCase();
            const clinicAddress = (clinic.address || '').toUpperCase();
            
            // Accept 3+ character postcode matches (e.g., "NW6", "W1C", "SW3")
            // Match if postcode starts with filter or contains it
            const postcodeMatch = clinicPostcode.includes(filterUpper) || 
                                 clinicPostcode.startsWith(filterUpper) ||
                                 clinicAddress.includes(filterUpper);
            
            if (!postcodeMatch) continue;
          }
          
          // Text search filter - enhanced to include area and postcode
          if (searchText) {
            const text = searchText.toLowerCase();
            const matches = 
              clinic.name?.toLowerCase().includes(text) ||
              clinic.address?.toLowerCase().includes(text) ||
              clinic.area?.toLowerCase().includes(text) ||
              clinic.postcode?.toLowerCase().includes(text) ||
              clinic.languages?.some(l => l.toLowerCase().includes(text)) ||
              clinic.services?.some(s => s.toLowerCase().includes(text));
            if (!matches) continue;
          }
          
          // Calculate match score
          const score = calculateMatchScore(clinic, searchText, selectedServices, selectedLanguages);
          if (score < minScore) continue;
          
          results.push({ 
            clinic, 
            match: { score, details: [], matched_services: [], matched_languages: [] }, 
            score 
          });
        }
        
        // Sort results
        if (sortBy === 'match') {
          results.sort((a, b) => b.score - a.score);
        } else if (sortBy === 'name') {
          results.sort((a, b) => a.clinic.name.localeCompare(b.clinic.name));
        } else if (sortBy === 'services') {
          results.sort((a, b) => (b.clinic.services?.length || 0) - (a.clinic.services?.length || 0));
        } else if (sortBy === 'rating') {
          results.sort((a, b) => (b.clinic.rating || 0) - (a.clinic.rating || 0));
        }
        
        // Limit results to MAX_RESULTS
        const limitedResults = results.slice(0, MAX_RESULTS);
        
        setResults(limitedResults);
        setCurrentPage(1); // Reset to first page on new search
      } catch (error) {
        console.error('Search error:', error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 100);
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
      emergency: false,
      children: false,
      wheelchair: false,
      parking: false
    });
    setMinScore(0);
    setMinRating(0);
    setSortBy('match');
    setCurrentPage(1);
  }
  
  // Pagination calculations
  const totalResults = results.length;
  const totalPages = Math.ceil(totalResults / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentResults = results.slice(startIndex, endIndex);
  
  // Debug logging
  useEffect(() => {
    console.log(`🔍 Results state: ${results.length} total, ${currentResults.length} on current page`);
    console.log(`🔍 Current page: ${currentPage}, Items per page: ${itemsPerPage}`);
    if (results.length > 0) {
      console.log(`🔍 First result in state:`, results[0]);
    }
  }, [results, currentPage, itemsPerPage]);
  
  // Handle page change
  function handlePageChange(page) {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  
  // Handle items per page change
  function handleItemsPerPageChange(newItemsPerPage) {
    setItemsPerPage(newItemsPerPage);
    setCurrentPage(1); // Reset to first page
  }
  
  // Generate page numbers for pagination
  function getPageNumbers() {
    const pages = [];
    const maxVisiblePages = 5;
    
    if (totalPages <= maxVisiblePages) {
      // Show all pages if total is less than max visible
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Show first page
      pages.push(1);
      
      if (currentPage > 3) {
        pages.push('...');
      }
      
      // Show pages around current page
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);
      
      for (let i = start; i <= end; i++) {
        if (!pages.includes(i)) {
          pages.push(i);
        }
      }
      
      if (currentPage < totalPages - 2) {
        pages.push('...');
      }
      
      // Show last page
      if (!pages.includes(totalPages)) {
        pages.push(totalPages);
      }
    }
    
    return pages;
  }

  function getScoreClass(score) {
    if (score >= 70) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
  }

  const hasActiveFilters = searchText || areaFilter || postcodeFilter || 
    selectedServices.length > 0 || selectedLanguages.length > 0 ||
    filters.emergency || filters.children || filters.wheelchair || filters.parking || minScore > 0 || minRating > 0;

  return (
    <div className="search-page">
      <div className="container">
        <div className="header">
          <h1>🔍 Private Dental Clinic Search</h1>
          <p>Find the perfect private dental clinic in London based on services and languages</p>
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
                placeholder="Search by name, address, language, or service (e.g., Spanish, Orthodontics)..."
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
                placeholder="Postcode (e.g., NW6, W1C, SW3)"
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
                        checked={filters.emergency}
                        onChange={(e) => setFilters({...filters, emergency: e.target.checked})}
                      />
                      <span>Emergency Services</span>
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
              <div className="results-stats">
                <div className="results-count">
                  Showing {startIndex + 1}-{Math.min(endIndex, totalResults)} of {totalResults} 
                  {totalResults >= MAX_RESULTS && ` (limited to ${MAX_RESULTS} max)`} clinic{totalResults !== 1 ? 's' : ''} found
                </div>
                <div className="results-controls">
                  <div className="items-per-page-selector">
                    <label htmlFor="itemsPerPage">Show:</label>
                    <select
                      id="itemsPerPage"
                      value={itemsPerPage}
                      onChange={(e) => handleItemsPerPageChange(Number(e.target.value))}
                      className="items-per-page-select"
                    >
                      <option value={25}>25</option>
                      <option value={50}>50</option>
                      <option value={100}>100</option>
                    </select>
                    <span>per page</span>
                  </div>
                </div>
              </div>
              <div className="progress-bar-container">
                <div className="progress-bar">
                  <div 
                    className="progress-bar-fill" 
                    style={{ width: `${(totalResults / Math.min(clinicsData.length, MAX_RESULTS)) * 100}%` }}
                  ></div>
                </div>
                <span className="progress-percentage">
                  {Math.round((totalResults / Math.min(clinicsData.length, MAX_RESULTS)) * 100)}%
                </span>
              </div>
            </div>
            <div className="results-container">
              {console.log(`🎨 Rendering ${currentResults.length} results on page ${currentPage}`)}
              {currentResults.length === 0 ? (
                <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
                  <p>No results to display on this page.</p>
                  <p>Total results: {totalResults}, Current page: {currentPage}, Items per page: {itemsPerPage}</p>
                </div>
              ) : (
                currentResults.map((result, index) => {
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
              }))}
            </div>
            
            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="pagination">
                <button
                  className="pagination-button"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  aria-label="Previous page"
                >
                  ← Previous
                </button>
                
                <div className="pagination-pages">
                  {getPageNumbers().map((page, idx) => {
                    if (page === '...') {
                      return <span key={`ellipsis-${idx}`} className="pagination-ellipsis">...</span>;
                    }
                    return (
                      <button
                        key={page}
                        className={`pagination-page ${currentPage === page ? 'active' : ''}`}
                        onClick={() => handlePageChange(page)}
                        aria-label={`Go to page ${page}`}
                        aria-current={currentPage === page ? 'page' : undefined}
                      >
                        {page}
                      </button>
                    );
                  })}
                </div>
                
                <button
                  className="pagination-button"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  aria-label="Next page"
                >
                  Next →
                </button>
              </div>
            )}
            
            {totalResults >= MAX_RESULTS && (
              <div className="results-limit-notice">
                <p>⚠️ Results limited to {MAX_RESULTS} clinics. Refine your search to see more specific results.</p>
              </div>
            )}
          </div>
        )}

        {results.length === 0 && !loading && (
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <h3>No results yet</h3>
            <p>Use the search form above to find dental clinics in London</p>
            <div style={{ marginTop: '20px', fontSize: '0.9em', color: '#666' }}>
              <p>Debug info:</p>
              <p>clinicsData length: {clinicsData?.length || 'undefined'}</p>
              <p>results length: {results.length}</p>
              <p>loading: {loading ? 'true' : 'false'}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Search;
>>>>>>> 7b08c46b2c93945ae5746e5ac7ad7018a1a7ab7e
