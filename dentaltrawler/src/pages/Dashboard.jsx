import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import { clinicsData } from '../clinics';
import './Dashboard.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend);

function Dashboard() {
  // Calculate statistics from embedded data
  const stats = useMemo(() => {
    const allServices = new Set();
    const allLanguages = new Set();
    const serviceCounts = {};
    const languageCounts = {};
    let totalServicesCount = 0;

    clinicsData.forEach(clinic => {
      const services = clinic.services || [];
      const languages = clinic.languages || [];

      services.forEach(service => {
        allServices.add(service);
        serviceCounts[service] = (serviceCounts[service] || 0) + 1;
      });

      languages.forEach(language => {
        allLanguages.add(language);
        languageCounts[language] = (languageCounts[language] || 0) + 1;
      });

      totalServicesCount += services.length;
    });

    const avgServices = clinicsData.length > 0 ? totalServicesCount / clinicsData.length : 0;

    return {
      total_clinics: clinicsData.length,
      total_services: allServices.size,
      total_languages: allLanguages.size,
      avg_services_per_clinic: Math.round(avgServices * 10) / 10,
      service_counts: serviceCounts,
      language_counts: languageCounts
    };
  }, []);


  // Prepare chart data
  const servicesData = {
    labels: Object.entries(stats.service_counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(s => s[0]),
    datasets: [{
      label: 'Number of Clinics',
      data: Object.entries(stats.service_counts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(s => s[1]),
      backgroundColor: 'rgba(102, 126, 234, 0.8)',
      borderColor: 'rgba(102, 126, 234, 1)',
      borderWidth: 1
    }]
  };

  const languagesData = {
    labels: Object.entries(stats.language_counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(l => l[0]),
    datasets: [{
      data: Object.entries(stats.language_counts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(l => l[1]),
      backgroundColor: [
        'rgba(102, 126, 234, 0.8)',
        'rgba(118, 75, 162, 0.8)',
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(199, 199, 199, 0.8)',
        'rgba(83, 102, 255, 0.8)'
      ]
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: false
      }
    }
  };

  const doughnutOptions = {
    ...chartOptions,
    plugins: {
      ...chartOptions.plugins,
      legend: {
        position: 'right'
      }
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1>🦷 London Dental Services Dashboard</h1>
        <p>Comprehensive overview of dental clinics, services, and languages</p>
        <div style={{ marginTop: '20px' }}>
          <Link to="/" style={{ color: '#667eea', textDecoration: 'none', fontWeight: '600' }}>
            ← Back to Search
          </Link>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="number">{stats.total_clinics}</div>
          <div className="label">Total Clinics</div>
        </div>
        <div className="stat-card">
          <div className="number">{stats.total_services}</div>
          <div className="label">Unique Services</div>
        </div>
        <div className="stat-card">
          <div className="number">{stats.total_languages}</div>
          <div className="label">Languages Spoken</div>
        </div>
        <div className="stat-card">
          <div className="number">{stats.avg_services_per_clinic}</div>
          <div className="label">Avg Services/Clinic</div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h2>Top Services Offered</h2>
          <div style={{ height: '300px' }}>
            <Bar data={servicesData} options={chartOptions} />
          </div>
        </div>
        <div className="chart-card">
          <h2>Languages Spoken</h2>
          <div style={{ height: '300px' }}>
            <Doughnut data={languagesData} options={doughnutOptions} />
          </div>
        </div>
      </div>

        <div className="clinics-list">
        <h2>Dental Clinics in London</h2>
        <div className="clinics-container">
          {clinicsData.map((clinic, index) => (
            <div key={index} className="clinic-card">
              <div className="clinic-name">{clinic.name || 'Unknown Clinic'}</div>
              {clinic.address && (
                <div className="clinic-info">
                  <svg viewBox="0 0 24 24">
                    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                  </svg>
                  {clinic.address}
                </div>
              )}
              {clinic.phone && (
                <div className="clinic-info">
                  <svg viewBox="0 0 24 24">
                    <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
                  </svg>
                  {clinic.phone}
                </div>
              )}
              {clinic.link && (
                <div className="clinic-info">
                  <svg viewBox="0 0 24 24">
                    <path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/>
                  </svg>
                  <a href={clinic.link} target="_blank" rel="noopener noreferrer" style={{ color: '#667eea' }}>
                    Visit Website
                  </a>
                </div>
              )}
              <div className="services-languages">
                <div className="services">
                  <h3>Services Provided</h3>
                  <div>
                    {clinic.services && clinic.services.length > 0 ? (
                      clinic.services.map(s => (
                        <span key={s} className="tag">{s}</span>
                      ))
                    ) : (
                      <span style={{ color: '#999' }}>No services listed</span>
                    )}
                  </div>
                </div>
                <div className="languages">
                  <h3>Languages Spoken</h3>
                  <div>
                    {clinic.languages && clinic.languages.length > 0 ? (
                      clinic.languages.map(l => (
                        <span key={l} className="tag language">{l}</span>
                      ))
                    ) : (
                      <span style={{ color: '#999' }}>No languages listed</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

