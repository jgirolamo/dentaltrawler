# Testing Locally - Quick Guide

## Prerequisites Check

First, verify Node.js is installed:
```bash
node --version  # Should show v20 or higher
npm --version   # Should show version number
```

If Node.js is not installed, install it:
- **macOS (using Homebrew)**: `brew install node`
- **Or download from**: https://nodejs.org/

## Steps to Test Locally

1. **Navigate to the frontend directory:**
   ```bash
   cd /Users/g/Projects/dentaltrawler/dentaltrawler
   ```

2. **Install dependencies (first time only):**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open in browser:**
   - The terminal will show: `Local: http://localhost:5173`
   - Open that URL in your browser

5. **Test the application:**
   - Search page should load at `/`
   - Dashboard should be available at `/dashboard`
   - Error logs page at `/error-logs`

## Quick Test Script

You can also use the provided script:
```bash
cd /Users/g/Projects/dentaltrawler
bash scripts/run_local.sh
```

## Troubleshooting

- **Port 5173 already in use?** Vite will automatically try the next available port
- **Dependencies issues?** Delete `node_modules` and `package-lock.json`, then run `npm install` again
- **Build errors?** Check that you have Node.js 20+ installed

## Expected Behavior

- ✅ React app loads without errors
- ✅ Search functionality works
- ✅ Dashboard displays clinic statistics
- ✅ Navigation between pages works
- ✅ No console errors in browser DevTools

