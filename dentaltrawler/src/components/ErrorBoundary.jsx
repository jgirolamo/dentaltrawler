import React from 'react';
import errorLogger from '../utils/errorLogger';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error
    errorLogger.logError(error, {
      type: 'react_error_boundary',
      componentStack: errorInfo.componentStack,
      errorInfo: errorInfo
    });

    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.handleReset);
      }

      // Default fallback UI
      return (
        <div style={{
          padding: '2rem',
          maxWidth: '800px',
          margin: '2rem auto',
          border: '1px solid #e0e0e0',
          borderRadius: '8px',
          backgroundColor: '#fff'
        }}>
          <h2 style={{ color: '#d32f2f', marginTop: 0 }}>⚠️ Something went wrong</h2>
          <p>An error occurred while rendering this component.</p>
          
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
              <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>Error Details</summary>
              <pre style={{ 
                marginTop: '1rem', 
                padding: '1rem', 
                backgroundColor: '#fff', 
                overflow: 'auto',
                fontSize: '12px',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word'
              }}>
                {this.state.error.toString()}
                {this.state.errorInfo && this.state.errorInfo.componentStack}
              </pre>
            </details>
          )}

          <div style={{ marginTop: '1.5rem' }}>
            <button 
              onClick={this.handleReset}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#1976d2',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                marginRight: '1rem'
              }}
            >
              Try Again
            </button>
            <button 
              onClick={() => window.location.reload()}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#666',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Reload Page
            </button>
          </div>

          <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#666' }}>
            Error has been logged. You can view logs in the browser console or download them.
          </p>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

