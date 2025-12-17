/**
 * Fetch real NHS dental clinic data at runtime
 * Uses NHS Service Finder API if available, or fetches from NHS website
 */

export async function fetchRealClinics(location = "London", limit = 50) {
  try {
    // Try NHS API endpoint (if available)
    const apiUrl = `https://www.nhs.uk/api/service-search/dentist?location=${encodeURIComponent(location)}&limit=${limit}`;
    
    const response = await fetch(apiUrl, {
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data && (Array.isArray(data) || data.results)) {
        const clinics = Array.isArray(data) ? data : data.results;
        return formatClinics(clinics);
      }
    }
  } catch (error) {
    console.log('API not available, trying alternative...');
  }
  
  // Alternative: Use NHS Service Finder search page
  // Note: This requires CORS proxy or backend scraping
  // For now, return empty and log instructions
  console.warn('Real-time NHS data fetching requires backend scraping.');
  console.warn('To get real data:');
  console.warn('1. Install Python dependencies: pip install -r requirements.txt');
  console.warn('2. Run scraper: python dental_trawler.py');
  console.warn('3. Copy dental_clinics_london.json to dentaltrawler/src/clinics.js');
  
  return [];
}

function formatClinics(clinics) {
  return clinics.map(clinic => ({
    name: clinic.name || clinic.practiceName || '',
    address: clinic.address || clinic.fullAddress || '',
    phone: clinic.phone || clinic.telephone || '',
    services: clinic.services || clinic.serviceTypes || [],
    languages: clinic.languages || [],
    postcode: extractPostcode(clinic.address || clinic.fullAddress || ''),
    nhs: clinic.acceptsNHS !== false,
    private: clinic.acceptsPrivate !== false,
    emergency: clinic.emergency || false,
    children: clinic.children || false,
    wheelchair_access: clinic.wheelchairAccess || false,
    rating: clinic.rating || 0
  }));
}

function extractPostcode(address) {
  const match = address.match(/([A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2})/);
  return match ? match[1] : '';
}

