import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import LiveSearch from './pages/LiveSearch';
import Search from './pages/Search';
import Dashboard from './pages/Dashboard';
import ErrorLogs from './pages/ErrorLogs';
import AllClinics from './pages/AllClinics';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <nav className="app-nav">
          <Link to="/">🔍 Live Search</Link>
          <Link to="/static">📋 Static Data</Link>
          <Link to="/dashboard">📊 Dashboard</Link>
          <Link to="/all-clinics">🦷 All Clinics</Link>
        </nav>
        <Routes>
          <Route path="/" element={<LiveSearch />} />
          <Route path="/static" element={<Search />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/error-logs" element={<ErrorLogs />} />
          <Route path="/all-clinics" element={<AllClinics />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
