# Local Debugging Guide

## Quick Start

### 1. Install Node.js and npm

If npm is not installed, install it:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install nodejs npm
```

**Or use Node Version Manager (nvm) - Recommended:**
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload shell
source ~/.bashrc

# Install Node.js (LTS version)
nvm install --lts
nvm use --lts
```

### 2. Install Dependencies

```bash
cd dentaltrawler
npm install
```

### 3. Run Development Server

```bash
npm run dev
```

The app will start at: `http://localhost:5173`

### 4. Open Browser and Debug

1. Open `http://localhost:5173` in your browser
2. Open Developer Tools (F12)
3. Go to Console tab
4. Look for:
   - `✅ Loaded X clinics` - confirms data loaded
   - `✅ Initial results set: X clinics` - confirms initial search worked
   - Any `❌` error messages

### 5. Test Search Functionality

1. Try searching for "Harley Street"
2. Try filtering by services (e.g., "Cosmetic Dentistry")
3. Try filtering by languages (e.g., "French")
4. Check console for any errors

## Debugging Checklist

### Check Data Loading
- [ ] Console shows `✅ Loaded X clinics`
- [ ] `clinicsData` is defined (check in console: `typeof clinicsData`)
- [ ] `clinicsData.length` is greater than 0

### Check Search Function
- [ ] Clicking search button triggers `performSearch()`
- [ ] Results appear after search
- [ ] No JavaScript errors in console

### Check Pagination
- [ ] Results show pagination controls (if > items per page)
- [ ] Page navigation works
- [ ] Items per page selector works

## Common Issues

### Issue: "Cannot find module '../clinics'"
**Fix**: Ensure `dentaltrawler/src/clinics.js` exists and has proper export:
```javascript
export const clinicsData = [...];
```

### Issue: "clinicsData is undefined"
**Fix**: Check import statement in `Search.jsx`:
```javascript
import { clinicsData } from '../clinics';
```

### Issue: Search returns no results
**Fix**: 
1. Check console for errors
2. Verify `clinicsData` has data
3. Check if filters are too restrictive

### Issue: Build fails
**Fix**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Testing Production Build Locally

To test the production build (like Vercel):

```bash
npm run build
npm run preview
```

Visit `http://localhost:4173` to test the production build.

## Browser Console Commands

You can test in the browser console:

```javascript
// Check if clinicsData is loaded
console.log(clinicsData);

// Check number of clinics
console.log(clinicsData.length);

// Check first clinic
console.log(clinicsData[0]);

// Test search manually
const results = clinicsData.filter(c => 
  c.name.toLowerCase().includes('harley')
);
console.log(results);
```

## Next Steps

If search works locally but not on Vercel:
1. Check Vercel build logs
2. Verify `clinics.js` is included in build
3. Check browser console on Vercel deployment
4. Compare local vs Vercel behavior

