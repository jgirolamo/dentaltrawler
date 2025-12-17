# Error Logging for Vercel

## Overview

This project includes a comprehensive error logging system that works with Vercel deployments. Errors are logged to:
- Browser console (development)
- localStorage (persistent across sessions)
- Vercel serverless function (optional, for production)

## Features

✅ **React Error Boundary** - Catches React component errors  
✅ **Global Error Handlers** - Catches unhandled errors and promise rejections  
✅ **Error Logger Utility** - Centralized error logging  
✅ **Error Logs Page** - View and download error logs  
✅ **Vercel Serverless Function** - Optional server-side logging  

## Setup

### 1. Environment Variables (Optional)

Add to your `.env` file or Vercel environment variables:

```bash
# Optional: Endpoint for server-side error logging
VITE_ERROR_LOG_ENDPOINT=/api/log-error

# Optional: Vercel build ID (automatically set by Vercel)
VITE_VERCEL_BUILD_ID=your-build-id
```

### 2. View Error Logs

Access the error logs page at:
```
https://your-app.vercel.app/error-logs
```

Or in development:
```
http://localhost:5173/error-logs
```

## Usage

### Automatic Error Logging

Errors are automatically logged when:
- React components throw errors (caught by ErrorBoundary)
- Unhandled JavaScript errors occur
- Unhandled promise rejections occur

### Manual Error Logging

```javascript
import errorLogger from './utils/errorLogger';

// Log an error
try {
  // Some code that might fail
} catch (error) {
  errorLogger.logError(error, {
    component: 'Search',
    action: 'performSearch',
    additionalInfo: 'User was searching for clinics'
  });
}

// Log a warning
errorLogger.logWarning('Low data quality', {
  source: 'NHS API',
  recordCount: 10
});

// Log info
errorLogger.logInfo('Data loaded successfully', {
  recordCount: 50
});
```

### Accessing Logs Programmatically

```javascript
import errorLogger from './utils/errorLogger';

// Get all logs
const logs = errorLogger.getLogs();

// Get logs as JSON string
const logsString = errorLogger.getLogsAsString();

// Clear all logs
errorLogger.clearLogs();

// Download logs as file
errorLogger.downloadLogs();
```

## Error Log Structure

Each error log contains:

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "message": "Error message",
  "stack": "Error stack trace",
  "context": {
    "component": "Search",
    "action": "performSearch"
  },
  "url": "https://your-app.vercel.app/search",
  "userAgent": "Mozilla/5.0...",
  "environment": "production",
  "buildId": "vercel-build-id"
}
```

## Vercel Serverless Function

The error logging includes a Vercel serverless function at `/api/log-error` that:
- Receives error logs from the client
- Logs to Vercel's server logs (visible in Vercel dashboard)
- Can be extended to save to a database or external service

### Viewing Logs in Vercel

1. Go to your Vercel dashboard
2. Select your project
3. Go to "Functions" tab
4. Click on `api/log-error`
5. View the logs in the "Logs" section

### Extending the Serverless Function

You can extend `/api/log-error.js` to:
- Save errors to a database (MongoDB, PostgreSQL, etc.)
- Send to external services (Sentry, LogRocket, etc.)
- Send email notifications for critical errors
- Aggregate error statistics

Example extension:

```javascript
// api/log-error.js
import { MongoClient } from 'mongodb';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const errorLog = req.body;

  // Save to MongoDB
  const client = await MongoClient.connect(process.env.MONGODB_URI);
  const db = client.db('error_logs');
  await db.collection('errors').insertOne(errorLog);
  await client.close();

  // Also log to Vercel
  console.error('🚨 Client Error:', JSON.stringify(errorLog, null, 2));

  return res.status(200).json({ success: true });
}
```

## Error Boundary

The `ErrorBoundary` component wraps your app and catches React errors. It provides:
- Fallback UI when errors occur
- Error details in development mode
- "Try Again" and "Reload Page" buttons

### Custom Error Boundary

You can provide a custom fallback:

```jsx
<ErrorBoundary
  fallback={(error, reset) => (
    <div>
      <h1>Custom Error UI</h1>
      <button onClick={reset}>Try Again</button>
    </div>
  )}
>
  <App />
</ErrorBoundary>
```

## Best Practices

1. **Log Context**: Always include relevant context when logging errors
2. **Don't Log Sensitive Data**: Avoid logging passwords, tokens, or personal information
3. **Rate Limiting**: The logger automatically limits to 100 logs to prevent memory issues
4. **Production vs Development**: Show detailed errors only in development
5. **Monitor Regularly**: Check error logs regularly to catch issues early

## Troubleshooting

### Logs Not Appearing

- Check browser console for errors
- Verify localStorage is enabled
- Check that ErrorBoundary is wrapping your app
- Verify the error logger is imported correctly

### Serverless Function Not Working

- Check Vercel function logs in dashboard
- Verify the route is configured in `vercel.json`
- Check that `VITE_ERROR_LOG_ENDPOINT` is set correctly
- Ensure CORS is handled if needed

### localStorage Full

- The logger automatically limits to 100 logs
- Use `errorLogger.clearLogs()` to clear old logs
- Download logs before clearing if you need to keep them

## Files

- `dentaltrawler/src/utils/errorLogger.js` - Main error logging utility
- `dentaltrawler/src/components/ErrorBoundary.jsx` - React error boundary
- `dentaltrawler/src/pages/ErrorLogs.jsx` - Error logs viewer page
- `api/log-error.js` - Vercel serverless function for server-side logging

## Next Steps

1. **Set up external logging service** (Sentry, LogRocket, etc.) for production
2. **Add error notifications** for critical errors
3. **Create error analytics dashboard** to track error trends
4. **Set up automated error reports** via email or Slack

