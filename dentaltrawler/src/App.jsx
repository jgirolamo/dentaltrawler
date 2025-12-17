import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import Search from './pages/Search';
import Dashboard from './pages/Dashboard';
import ErrorLogs from './pages/ErrorLogs';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Search />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/error-logs" element={<ErrorLogs />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
