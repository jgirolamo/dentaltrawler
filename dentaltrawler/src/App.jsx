import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import Search from './pages/Search';
import Dashboard from './pages/Dashboard';
import ErrorLogs from './pages/ErrorLogs';
import AllClinics from './pages/AllClinics';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Search />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/error-logs" element={<ErrorLogs />} />
          <Route path="/all-clinics" element={<AllClinics />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
