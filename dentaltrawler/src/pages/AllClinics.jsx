import { useState } from 'react';
import { Link } from 'react-router-dom';
import { clinicsData } from '../clinics';
import { getZone } from '../utils/zoneUtils';
import './AllClinics.css';

function AllClinics() {
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(50);

  // Pagination calculations
  const totalResults = clinicsData.length;
  const totalPages = Math.ceil(totalResults / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentClinics = clinicsData.slice(startIndex, endIndex);

  function handlePageChange(page) {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function handleItemsPerPageChange(newItemsPerPage) {
    setItemsPerPage(newItemsPerPage);
    setCurrentPage(1);
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
    <div className="all-clinics-page">
      <div className="container">
        <div className="header">
          <h1>🦷 All Dental Clinics</h1>
          <p>Complete list of {clinicsData.length} dental clinics in London</p>
          <div style={{ marginTop: '20px' }}>
            <Link to="/" style={{ color: '#667eea', textDecoration: 'none', fontWeight: '600' }}>
              ← Back to Search
            </Link>
          </div>
        </div>

        <div className="clinics-list-container">
          <div className="results-header">
            <h2>
              Showing {startIndex + 1}-{Math.min(endIndex, totalResults)} of {totalResults} clinics
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

          <div className="clinics-grid">
            {currentClinics.map((clinic, index) => {
              const zone = getZone(clinic);
              return (
              <div key={index} className="clinic-card">
                <div className="clinic-header">
                  <h3>{clinic.name || 'Unknown Clinic'}</h3>
                  {zone && (
                    <span className={`zone-badge zone-${zone}`}>
                      Zone {zone}
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

                {clinic.source && (
                  <div className="clinic-source">
                    <small>Source: {clinic.source}</small>
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
                Page {currentPage} of {totalPages} ({totalResults} total clinics)
              </div>
            </div>
          )}
        </div>
      </div>
      <Link to="/error-logs" className="error-logs-link-fixed" title="Error Logs">
        📋
      </Link>
      <Link to="/all-clinics" className="all-clinics-link-fixed" title="All Clinics">
        🦷
      </Link>
    </div>
  );
}

export default AllClinics;

