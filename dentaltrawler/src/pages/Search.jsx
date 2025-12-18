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
    }

    // Service filter (30 points)
    if (selectedServices.length > 0) {
      const clinicServices = (clinic.services || []).map(s => s.toLowerCase());
      let serviceMatches = 0;
      selectedServices.forEach(service => {
        if (clinicServices.some(cs => cs.includes(service.toLowerCase()))) {
          serviceMatches++;
          matchedServices.push(service);
        }
      });
      if (serviceMatches > 0) {
        score += (serviceMatches / selectedServices.length) * 30;
        matchDetails.push(`${serviceMatches} service(s) match`);
      }
    }

    // Language filter (20 points)
    if (selectedLanguages.length > 0) {
      const clinicLanguages = (clinic.languages || []).map(l => l.toLowerCase());
      let languageMatches = 0;
      selectedLanguages.forEach(language => {
        if (clinicLanguages.some(cl => cl.includes(language.toLowerCase()))) {
          languageMatches++;
          matchedLanguages.push(language);
        }
      });
      if (languageMatches > 0) {
        score += (languageMatches / selectedLanguages.length) * 20;
        matchDetails.push(`${languageMatches} language(s) match`);
      }
    }

    // Area filter (10 points)
    if (areaFilter) {
      const clinicArea = (clinic.area || '').toLowerCase();
      if (clinicArea.includes(areaFilter.toLowerCase())) {
        score += 10;
        matchDetails.push('Area matches');
      }
    }

    // Postcode filter (10 points)
    if (postcodeFilter) {
      const clinicPostcode = (clinic.postcode || '').toLowerCase();
      if (clinicPostcode.includes(postcodeFilter.toLowerCase())) {
        score += 10;
        matchDetails.push('Postcode matches');
      }
    }

    return {
      score: Math.min(score, maxScore),
      matchDetails,
      matchedServices,
      matchedLanguages
    };
  }

  function performSearch() {
    setLoading(true);
    
    // Use setTimeout to avoid blocking UI
    setTimeout(() => {
      try {
        if (!clinicsData || clinicsData.length === 0) {
          console.error('❌ clinicsData is not loaded or empty');
          setResults([]);
          setLoading(false);
          return;
        }

        let filtered = [...clinicsData];

        // Text search filter
        if (searchText) {
          const text = searchText.toLowerCase();
          filtered = filtered.filter(clinic => {
            const name = (clinic.name || '').toLowerCase();
            const address = (clinic.address || '').toLowerCase();
            const languages = (clinic.languages || []).map(l => l.toLowerCase()).join(' ');
            const services = (clinic.services || []).map(s => s.toLowerCase()).join(' ');
            return name.includes(text) || address.includes(text) || 
                   languages.includes(text) || services.includes(text);
          });
        }

        // Area filter
        if (areaFilter) {
          filtered = filtered.filter(clinic => {
            const area = (clinic.area || '').toLowerCase();
            return area.includes(areaFilter.toLowerCase());
          });
        }

        // Postcode filter
        if (postcodeFilter) {
          filtered = filtered.filter(clinic => {
            const postcode = (clinic.postcode || '').toLowerCase();
            return postcode.includes(postcodeFilter.toLowerCase());
          });
        }

        // Service filter
        if (selectedServices.length > 0) {
          filtered = filtered.filter(clinic => {
            const clinicServices = (clinic.services || []).map(s => s.toLowerCase());
            return selectedServices.some(service => 
              clinicServices.some(cs => cs.includes(service.toLowerCase()))
            );
          });
        }

        // Language filter
        if (selectedLanguages.length > 0) {
          filtered = filtered.filter(clinic => {
            const clinicLanguages = (clinic.languages || []).map(l => l.toLowerCase());
            return selectedLanguages.some(language => 
              clinicLanguages.some(cl => cl.includes(language.toLowerCase()))
            );
          });
        }

        // Boolean filters
        if (filters.nhs) {
          filtered = filtered.filter(clinic => clinic.nhs === true);
        }
        if (filters.private) {
          filtered = filtered.filter(clinic => clinic.private === true);
        }
        if (filters.emergency) {
          filtered = filtered.filter(clinic => clinic.emergency === true);
        }
        if (filters.children) {
          filtered = filtered.filter(clinic => clinic.children === true);
        }
        if (filters.wheelchair) {
          filtered = filtered.filter(clinic => clinic.wheelchair_access === true);
        }
        if (filters.parking) {
          filtered = filtered.filter(clinic => clinic.parking === true);
        }

        // Score filter
        if (minScore > 0) {
          filtered = filtered.filter(clinic => {
            const match = calculateMatchScore(clinic, searchText, selectedServices, selectedLanguages);
            return match.score >= minScore;
          });
        }

        // Rating filter
        if (minRating > 0) {
          filtered = filtered.filter(clinic => {
            const rating = clinic.rating || 0;
            return rating >= minRating;
          });
        }

        // Calculate match scores
        const scoredResults = filtered.map(clinic => {
          const match = calculateMatchScore(clinic, searchText, selectedServices, selectedLanguages);
          return {
            clinic: clinic,
            match: match,
            score: match.score
          };
        });

        // Sort results
        let sortedResults = [...scoredResults];
        if (sortBy === 'match') {
          sortedResults.sort((a, b) => b.score - a.score);
        } else if (sortBy === 'name') {
          sortedResults.sort((a, b) => (a.clinic.name || '').localeCompare(b.clinic.name || ''));
        } else if (sortBy === 'rating') {
          sortedResults.sort((a, b) => (b.clinic.rating || 0) - (a.clinic.rating || 0));
        }

        // Limit results
        const limitedResults = sortedResults.slice(0, MAX_RESULTS);
        setResults(limitedResults);
        setLoading(false);
      } catch (error) {
        console.error('❌ Error processing clinic data:', error);
        setResults([]);
        setLoading(false);
      }
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
            <Link to="/error-logs" className="error-logs-link" style={{ marginLeft: '1rem', fontSize: '0.9rem', color: '#666' }}>
              📋 Error Logs
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
              <button className="search-button" onClick={performSearch}>
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </div>

          <div className="filters-toggle">
            <button 
              className="toggle-filters-btn"
              onClick={() => setShowFilters(!showFilters)}
            >
              {showFilters ? '▼' : '▶'} Advanced Filters
            </button>
            {hasActiveFilters && (
              <button className="clear-filters-btn" onClick={clearFilters}>
                Clear All Filters
              </button>
            )}
          </div>

          {showFilters && (
            <div className="filters-panel">
              <div className="filter-group">
                <label>Area:</label>
                <input
                  type="text"
                  placeholder="e.g., Westminster, Camden"
                  value={areaFilter}
                  onChange={(e) => setAreaFilter(e.target.value)}
                />
              </div>

              <div className="filter-group">
                <label>Postcode:</label>
                <input
                  type="text"
                  placeholder="e.g., SW1A, W1G"
                  value={postcodeFilter}
                  onChange={(e) => setPostcodeFilter(e.target.value)}
                />
              </div>

              <div className="filter-group">
                <label>Services:</label>
                <div className="checkbox-list">
                  {services.map(service => (
                    <label key={service} className="checkbox-item">
                      <input
                        type="checkbox"
                        checked={selectedServices.includes(service)}
                        onChange={() => toggleService(service)}
                      />
                      {service}
                    </label>
                  ))}
                </div>
              </div>

              <div className="filter-group">
                <label>Languages:</label>
                <div className="checkbox-list">
                  {languages.map(language => (
                    <label key={language} className="checkbox-item">
                      <input
                        type="checkbox"
                        checked={selectedLanguages.includes(language)}
                        onChange={() => toggleLanguage(language)}
                      />
                      {language}
                    </label>
                  ))}
                </div>
              </div>

              <div className="filter-group">
                <label>Type:</label>
                <div className="checkbox-list">
                  <label className="checkbox-item">
                    <input
                      type="checkbox"
                      checked={filters.nhs}
                      onChange={(e) => setFilters({...filters, nhs: e.target.checked})}
                    />
                    NHS
                  </label>
                  <label className="checkbox-item">
                    <input
                      type="checkbox"
                      checked={filters.private}
                      onChange={(e) => setFilters({...filters, private: e.target.checked})}
                    />
                    Private
                  </label>
                </div>
              </div>

              <div className="filter-group">
                <label>Features:</label>
                <div className="checkbox-list">
                  <label className="checkbox-item">
                    <input
                      type="checkbox"
                      checked={filters.emergency}
                      onChange={(e) => setFilters({...filters, emergency: e.target.checked})}
                    />
                    Emergency
                  </label>
                  <label className="checkbox-item">
                    <input
                      type="checkbox"
                      checked={filters.children}
                      onChange={(e) => setFilters({...filters, children: e.target.checked})}
                    />
                    Children
                  </label>
                  <label className="checkbox-item">
                    <input
                      type="checkbox"
                      checked={filters.wheelchair}
                      onChange={(e) => setFilters({...filters, wheelchair: e.target.checked})}
                    />
                    Wheelchair Access
                  </label>
                  <label className="checkbox-item">
                    <input
                      type="checkbox"
                      checked={filters.parking}
                      onChange={(e) => setFilters({...filters, parking: e.target.checked})}
                    />
                    Parking
                  </label>
                </div>
              </div>

              <div className="filter-group">
                <label>Min Score:</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={minScore}
                  onChange={(e) => setMinScore(Number(e.target.value))}
                />
              </div>

              <div className="filter-group">
                <label>Min Rating:</label>
                <input
                  type="number"
                  min="0"
                  max="5"
                  step="0.1"
                  value={minRating}
                  onChange={(e) => setMinRating(Number(e.target.value))}
                />
              </div>

              <div className="filter-group">
                <label>Sort By:</label>
                <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                  <option value="match">Match Score</option>
                  <option value="name">Name</option>
                  <option value="rating">Rating</option>
                </select>
              </div>
            </div>
          )}
        </div>

        <div className="results-section">
          <div className="results-header">
            <h2>
              {loading ? 'Searching...' : `Found ${totalResults} clinic${totalResults !== 1 ? 's' : ''}`}
            </h2>
            {totalResults > 0 && (
              <div className="items-per-page-selector">
                <label>Show:</label>
                <select 
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
            )}
          </div>

          {totalResults > MAX_RESULTS && (
            <div className="results-limit-notice">
              Showing top {MAX_RESULTS} results. Refine your search to see more.
            </div>
          )}

          {loading ? (
            <div className="loading">Loading...</div>
          ) : currentResults.length === 0 ? (
            <div className="no-results">
              <p>No clinics found matching your criteria.</p>
              <p>Try adjusting your filters or search terms.</p>
            </div>
          ) : (
            <>
              <div className="results-grid">
                {currentResults.map((result, index) => {
                  const clinic = result.clinic;
                  const match = result.match;
                  return (
                    <div key={index} className="clinic-card">
                      <div className="clinic-header">
                        <h3>{clinic.name || 'Unknown Clinic'}</h3>
                        {match.score > 0 && (
                          <span className={`match-score ${getScoreClass(match.score)}`}>
                            {match.score}% match
                          </span>
                        )}
                      </div>
                      
                      <div className="clinic-info">
                        {clinic.address && (
                          <div className="info-item">
                            <span className="info-label">📍 Address:</span>
                            <span>{clinic.address}</span>
                          </div>
                        )}
                        {clinic.phone && (
                          <div className="info-item">
                            <span className="info-label">📞 Phone:</span>
                            <span>{clinic.phone}</span>
                          </div>
                        )}
                        {clinic.area && (
                          <div className="info-item">
                            <span className="info-label">🏘️ Area:</span>
                            <span>{clinic.area}</span>
                          </div>
                        )}
                        {clinic.postcode && (
                          <div className="info-item">
                            <span className="info-label">📮 Postcode:</span>
                            <span>{clinic.postcode}</span>
                          </div>
                        )}
                        {clinic.rating && (
                          <div className="info-item">
                            <span className="info-label">⭐ Rating:</span>
                            <span>{clinic.rating}/5</span>
                          </div>
                        )}
                      </div>

                      {clinic.services && clinic.services.length > 0 && (
                        <div className="clinic-services">
                          <strong>Services:</strong>
                          <div className="tags">
                            {clinic.services.map((service, i) => (
                              <span key={i} className="tag">{service}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      {clinic.languages && clinic.languages.length > 0 && (
                        <div className="clinic-languages">
                          <strong>Languages:</strong>
                          <div className="tags">
                            {clinic.languages.map((language, i) => (
                              <span key={i} className="tag">{language}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="clinic-features">
                        {clinic.private && <span className="feature-badge">Private</span>}
                        {clinic.nhs && <span className="feature-badge">NHS</span>}
                        {clinic.emergency && <span className="feature-badge">Emergency</span>}
                        {clinic.children && <span className="feature-badge">Children</span>}
                        {clinic.wheelchair_access && <span className="feature-badge">Wheelchair</span>}
                        {clinic.parking && <span className="feature-badge">Parking</span>}
                      </div>

                      {clinic.link && (
                        <div className="clinic-link">
                          <a href={clinic.link} target="_blank" rel="noopener noreferrer">
                            Visit Website →
                          </a>
                        </div>
                      )}

                      {match.matchDetails && match.matchDetails.length > 0 && (
                        <div className="match-details">
                          <small>Match: {match.matchDetails.join(', ')}</small>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {totalPages > 1 && (
                <div className="pagination">
                  <div className="pagination-controls">
                    <button
                      className="pagination-button"
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                    >
                      ← Previous
                    </button>
                    
                    <div className="pagination-pages">
                      {getPageNumbers().map((page, index) => {
                        if (page === 'ellipsis') {
                          return <span key={`ellipsis-${index}`} className="pagination-ellipsis">...</span>;
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
                  
                  <div className="pagination-info">
                    Page {currentPage} of {totalPages} ({totalResults} total results)
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Search;
