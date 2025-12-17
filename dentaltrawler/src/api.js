/**
 * API client for Dental Clinic API
 */

// Use relative paths in production (same domain), or env variable, or localhost for dev
const API_BASE = import.meta.env.VITE_API_URL || 
  (import.meta.env.PROD ? '' : 'http://localhost:8000');

export const api = {
  async getClinics(limit = null, offset = 0) {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit);
    if (offset) params.append('offset', offset);
    
    const url = `${API_BASE}/api/clinics${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch clinics');
    return response.json();
  },

  async searchClinics(searchRequest) {
    const response = await fetch(`${API_BASE}/api/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(searchRequest)
    });
    if (!response.ok) throw new Error('Search failed');
    return response.json();
  },

  async getStatistics() {
    const response = await fetch(`${API_BASE}/api/statistics`);
    if (!response.ok) throw new Error('Failed to fetch statistics');
    return response.json();
  },

  async getServices() {
    const response = await fetch(`${API_BASE}/api/services`);
    if (!response.ok) throw new Error('Failed to fetch services');
    return response.json();
  },

  async getLanguages() {
    const response = await fetch(`${API_BASE}/api/languages`);
    if (!response.ok) throw new Error('Failed to fetch languages');
    return response.json();
  },

  async getMetadata() {
    const response = await fetch(`${API_BASE}/api/metadata`);
    if (!response.ok) throw new Error('Failed to fetch metadata');
    return response.json();
  }
};

