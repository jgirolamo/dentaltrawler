import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import errorLogger from '../utils/errorLogger';
import './ErrorLogs.css';

function ErrorLogs() {
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState('all'); // all, error, warning, info

  useEffect(() => {
    setLogs(errorLogger.getLogs());
  }, []);

  const filteredLogs = logs.filter(log => {
    if (filter === 'all') return true;
    return log.level === filter || (!log.level && filter === 'error');
  });

  const handleClear = () => {
    if (window.confirm('Are you sure you want to clear all error logs?')) {
      errorLogger.clearLogs();
      setLogs([]);
    }
  };

  const handleDownload = () => {
    errorLogger.downloadLogs();
  };

  const errorCount = logs.filter(log => !log.level || log.level === 'error').length;
  const warningCount = logs.filter(log => log.level === 'warning').length;

  return (
    <div className="error-logs-container">
      <div className="error-logs-header">
        <h1>Error Logs</h1>
        <div className="error-logs-stats">
          <span className="stat-error">Errors: {errorCount}</span>
          <span className="stat-warning">Warnings: {warningCount}</span>
          <span className="stat-total">Total: {logs.length}</span>
        </div>
      </div>

      <div className="error-logs-controls">
        <select 
          value={filter} 
          onChange={(e) => setFilter(e.target.value)}
          className="error-logs-filter"
        >
          <option value="all">All Logs</option>
          <option value="error">Errors Only</option>
          <option value="warning">Warnings Only</option>
        </select>
        
        <button onClick={handleDownload} className="btn-download">
          📥 Download Logs
        </button>
        
        <button onClick={handleClear} className="btn-clear">
          🗑️ Clear All
        </button>
      </div>

      <div className="error-logs-list">
        {filteredLogs.length === 0 ? (
          <div className="no-logs">
            <p>No {filter === 'all' ? '' : filter} logs found.</p>
            <p className="hint">Errors will appear here when they occur.</p>
          </div>
        ) : (
          filteredLogs.map((log, index) => (
            <div 
              key={index} 
              className={`error-log-item ${log.level || 'error'}`}
            >
              <div className="error-log-header">
                <span className="error-log-time">
                  {new Date(log.timestamp).toLocaleString()}
                </span>
                {log.level && (
                  <span className={`error-log-level ${log.level}`}>
                    {log.level.toUpperCase()}
                  </span>
                )}
              </div>
              
              <div className="error-log-message">
                {log.message}
              </div>

              {log.context && Object.keys(log.context).length > 0 && (
                <details className="error-log-details">
                  <summary>Context</summary>
                  <pre>{JSON.stringify(log.context, null, 2)}</pre>
                </details>
              )}

              {log.stack && (
                <details className="error-log-details">
                  <summary>Stack Trace</summary>
                  <pre className="error-log-stack">{log.stack}</pre>
                </details>
              )}

              {log.url && (
                <div className="error-log-meta">
                  <span>URL: {log.url}</span>
                </div>
              )}
            </div>
          ))
        )}
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

export default ErrorLogs;

