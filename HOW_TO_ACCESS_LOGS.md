# How to Access Error Logs

## 📋 Multiple Ways to Access Logs

### 1. **Error Logs Page (Easiest)** ⭐

Access the built-in error logs viewer in your app:

**URL:** `https://your-app.vercel.app/error-logs`

**In Development:**
```
http://localhost:5173/error-logs
```

**Features:**
- View all error logs in a nice UI
- Filter by type (errors, warnings, all)
- See error counts and statistics
- Download logs as JSON file
- Clear logs
- View stack traces and context

**Screenshot Preview:**
- Header with error statistics
- Filter dropdown
- Download and Clear buttons
- List of all errors with details

---

### 2. **Browser Console** (Development)

Open browser DevTools (F12) and check the console:

```javascript
// Errors are automatically logged to console
// Look for messages like:
🚨 Error Logged: { ... }
⚠️ Warning: { ... }
ℹ️ Info: { ... }
```

**To view stored logs:**
```javascript
// In browser console
import errorLogger from './utils/errorLogger';
errorLogger.getLogs();
```

---

### 3. **Browser localStorage** (Direct Access)

Logs are stored in browser's localStorage:

**In Browser Console:**
```javascript
// View raw logs
JSON.parse(localStorage.getItem('vercel_error_logs'))

// Or prettier:
console.table(JSON.parse(localStorage.getItem('vercel_error_logs')))
```

**Location:**
- Browser DevTools → Application tab → Local Storage → `vercel_error_logs`

---

### 4. **Vercel Dashboard** (Server-Side Logs)

For errors sent to the serverless function:

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to **"Functions"** tab
4. Click on **`api/log-error`**
5. View **"Logs"** section

**What you'll see:**
- All errors sent from client
- Timestamp
- Full error details
- Request information

**Note:** Only works if `VITE_ERROR_LOG_ENDPOINT` is set in environment variables.

---

### 5. **Programmatic Access** (In Code)

Access logs from your React components:

```javascript
import errorLogger from '../utils/errorLogger';

// Get all logs
const logs = errorLogger.getLogs();
console.log('All logs:', logs);

// Get logs as JSON string
const logsString = errorLogger.getLogsAsString();
console.log(logsString);

// Filter logs
const errors = logs.filter(log => !log.level || log.level === 'error');
const warnings = logs.filter(log => log.level === 'warning');

// Get latest error
const latestError = logs[0];
```

---

### 6. **Download Logs as File**

**From Error Logs Page:**
- Click "📥 Download Logs" button
- Saves as: `vercel-error-logs-YYYY-MM-DD.json`

**Programmatically:**
```javascript
import errorLogger from './utils/errorLogger';
errorLogger.downloadLogs();
```

---

### 7. **Vercel CLI** (Command Line)

If you have Vercel CLI installed:

```bash
# View function logs
vercel logs --follow

# View specific function
vercel logs api/log-error --follow
```

---

## 🔍 Quick Access Guide

### For Development:
1. **Open app** → Navigate to `/error-logs`
2. **Or** open browser console (F12)

### For Production:
1. **Vercel Dashboard** → Functions → `api/log-error` → Logs
2. **Or** visit `https://your-app.vercel.app/error-logs`

### For Debugging:
1. **Browser Console** → Check localStorage
2. **Or** use programmatic access in code

---

## 📊 Log Structure

Each log entry contains:

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

---

## 🎯 Recommended Workflow

### Daily Monitoring:
1. Check Vercel Dashboard → Functions → Logs
2. Or visit `/error-logs` page

### Debugging Specific Issue:
1. Open browser console
2. Check localStorage for recent errors
3. Use Error Logs page for detailed view

### Production Monitoring:
1. Set up Vercel Dashboard alerts
2. Regularly check `/error-logs` page
3. Download logs periodically for analysis

---

## 🔧 Troubleshooting

### Logs Not Showing?

1. **Check localStorage is enabled:**
   ```javascript
   // In console
   typeof localStorage !== 'undefined'
   ```

2. **Check ErrorBoundary is wrapping app:**
   - Should be in `App.jsx`

3. **Check error logger is imported:**
   - Should be in `main.jsx` or `App.jsx`

4. **Check browser console for errors:**
   - Errors should appear automatically

### Server Logs Not Working?

1. **Check environment variable:**
   ```bash
   # Should be set in Vercel
   VITE_ERROR_LOG_ENDPOINT=/api/log-error
   ```

2. **Check Vercel function:**
   - Go to Functions tab
   - Verify `api/log-error.js` exists
   - Check function logs

3. **Check network tab:**
   - Should see POST requests to `/api/log-error`

---

## 📝 Example: Accessing Logs in Code

```javascript
// In any React component
import { useEffect } from 'react';
import errorLogger from '../utils/errorLogger';

function MyComponent() {
  useEffect(() => {
    // Get all errors
    const logs = errorLogger.getLogs();
    console.log('Current errors:', logs);
    
    // Get only errors (not warnings)
    const errors = logs.filter(log => !log.level || log.level === 'error');
    console.log('Errors only:', errors);
    
    // Get errors from last hour
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
    const recentErrors = logs.filter(log => 
      new Date(log.timestamp) > oneHourAgo
    );
    console.log('Recent errors:', recentErrors);
  }, []);
  
  return <div>...</div>;
}
```

---

## 🚀 Quick Start

**Right now, you can:**

1. **Start your dev server:**
   ```bash
   cd dentaltrawler && npm run dev
   ```

2. **Visit error logs page:**
   ```
   http://localhost:5173/error-logs
   ```

3. **Or open browser console:**
   - Press F12
   - Check Console tab
   - Errors will appear automatically

That's it! Logs are accessible immediately. 🎉

