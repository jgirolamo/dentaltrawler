/**
 * Error Logger for Vercel
 * Logs errors to console, localStorage, and optionally to a server endpoint
 */

class ErrorLogger {
  constructor() {
    this.logs = [];
    this.maxLogs = 100; // Keep last 100 errors
    this.loadFromStorage();
    
    // Set up automatic saving
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', () => {
        this.saveToStorage();
      });
    }
  }

  /**
   * Log an error
   * @param {Error|string} error - The error object or message
   * @param {Object} context - Additional context (component, action, etc.)
   */
  logError(error, context = {}) {
    const errorLog = {
      timestamp: new Date().toISOString(),
      message: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : null,
      context: context,
      url: typeof window !== 'undefined' ? window.location.href : 'unknown',
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
      environment: import.meta.env.MODE || 'production',
      buildId: import.meta.env.VITE_VERCEL_BUILD_ID || 'unknown'
    };

    // Add to logs
    this.logs.unshift(errorLog);
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(0, this.maxLogs);
    }

    // Log to console
    console.error('🚨 Error Logged:', errorLog);

    // Save to localStorage
    this.saveToStorage();

    // Send to server if endpoint is configured
    this.sendToServer(errorLog);

    return errorLog;
  }

  /**
   * Log a warning
   */
  logWarning(message, context = {}) {
    const warningLog = {
      timestamp: new Date().toISOString(),
      level: 'warning',
      message: String(message),
      context: context,
      url: typeof window !== 'undefined' ? window.location.href : 'unknown'
    };

    console.warn('⚠️ Warning:', warningLog);
    this.logs.unshift(warningLog);
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(0, this.maxLogs);
    }
    this.saveToStorage();
  }

  /**
   * Log info
   */
  logInfo(message, context = {}) {
    const infoLog = {
      timestamp: new Date().toISOString(),
      level: 'info',
      message: String(message),
      context: context
    };

    console.info('ℹ️ Info:', infoLog);
  }

  /**
   * Save logs to localStorage
   */
  saveToStorage() {
    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        localStorage.setItem('vercel_error_logs', JSON.stringify(this.logs));
      } catch (e) {
        console.error('Failed to save logs to localStorage:', e);
      }
    }
  }

  /**
   * Load logs from localStorage
   */
  loadFromStorage() {
    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        const stored = localStorage.getItem('vercel_error_logs');
        if (stored) {
          this.logs = JSON.parse(stored);
        }
      } catch (e) {
        console.error('Failed to load logs from localStorage:', e);
      }
    }
  }

  /**
   * Send error to server endpoint (if configured)
   */
  async sendToServer(errorLog) {
    const endpoint = import.meta.env.VITE_ERROR_LOG_ENDPOINT;
    
    if (!endpoint) {
      // No endpoint configured, skip
      return;
    }

    try {
      await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(errorLog),
        // Don't wait for response to avoid blocking
        keepalive: true
      });
    } catch (e) {
      // Silently fail - don't log errors about logging errors
      console.debug('Failed to send error to server:', e);
    }
  }

  /**
   * Get all logs
   */
  getLogs() {
    return this.logs;
  }

  /**
   * Get logs as formatted string
   */
  getLogsAsString() {
    return JSON.stringify(this.logs, null, 2);
  }

  /**
   * Clear all logs
   */
  clearLogs() {
    this.logs = [];
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem('vercel_error_logs');
    }
  }

  /**
   * Download logs as file
   */
  downloadLogs() {
    const dataStr = this.getLogsAsString();
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `vercel-error-logs-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}

// Create singleton instance
const errorLogger = new ErrorLogger();

// Set up global error handlers
if (typeof window !== 'undefined') {
  // Handle unhandled errors
  window.addEventListener('error', (event) => {
    errorLogger.logError(event.error || event.message, {
      type: 'unhandled_error',
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno
    });
  });

  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    errorLogger.logError(event.reason, {
      type: 'unhandled_promise_rejection',
      promise: event.promise
    });
  });
}

export default errorLogger;

