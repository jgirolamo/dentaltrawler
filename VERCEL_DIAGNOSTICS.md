# Vercel Diagnostics Guide

## Quick Start

### 1. Get Vercel Token

1. Go to [Vercel Account Tokens](https://vercel.com/account/tokens)
2. Click "Create Token"
3. Give it a name (e.g., "Diagnostics")
4. Copy the token

### 2. Run Diagnostics

**Option A: Using Environment Variable**
```bash
export VERCEL_TOKEN=your_token_here
python3 scripts/check_vercel_status.py
```

**Option B: Pass Token Directly**
```bash
python3 scripts/check_vercel_status.py --token your_token_here
```

**Option C: Check Specific Project**
```bash
python3 scripts/check_vercel_status.py --project your-project-name
```

## What It Checks

The diagnostic script will:

✅ **Project Status**
- Find your project
- Show project ID and URL
- List recent deployments

✅ **Deployment Status**
- Check deployment states (READY, ERROR, BUILDING, etc.)
- Show deployment URLs
- Display creation timestamps

✅ **Build Logs**
- Show build events
- Display errors and warnings
- Check build configuration

✅ **Function Logs**
- Check serverless function status
- View function execution logs
- Identify function errors

## Example Output

```
============================================================
🔍 Diagnosing Vercel Project: dentaltrawler
============================================================

✅ Project found: dentaltrawler
   ID: prj_xxxxx
   URL: dentaltrawler.vercel.app

📦 Recent Deployments (5):

1. ✅ READY
   ID: dpl_xxxxx
   URL: https://dentaltrawler.vercel.app
   Created: 2024-01-15T10:30:00.000Z

2. ❌ ERROR
   ID: dpl_yyyyy
   URL: https://dentaltrawler-git-main.vercel.app
   Created: 2024-01-15T09:00:00.000Z
   ⚠️  ERROR STATE - Checking logs...
   ❌ Found 2 error events
      - Error: Build failed...
```

## Common Issues & Fixes

### Issue: "Project not found"

**Solution:**
- Check project name matches exactly
- List all projects: The script will show available projects

### Issue: "VERCEL_TOKEN not found"

**Solution:**
1. Get token from https://vercel.com/account/tokens
2. Set environment variable: `export VERCEL_TOKEN=your_token`
3. Or pass with `--token` flag

### Issue: Deployment in ERROR state

**What to check:**
1. Build logs will show the error
2. Common causes:
   - Build command failure
   - Missing dependencies
   - Syntax errors
   - Environment variable issues

**Fix:**
- Check the error message in build logs
- Verify `package.json` and build configuration
- Check environment variables in Vercel dashboard

### Issue: Function not working

**What to check:**
1. Function logs will show errors
2. Common causes:
   - Missing environment variables
   - Runtime errors
   - Timeout issues

**Fix:**
- Check function logs in output
- Verify `api/log-error.js` exists
- Check function timeout settings

## Manual Checks

### Via Vercel Dashboard

1. **Check Deployments:**
   - Go to https://vercel.com/dashboard
   - Select your project
   - Click "Deployments" tab
   - Click on a deployment to see details

2. **Check Build Logs:**
   - Open a deployment
   - Click "Build Logs" tab
   - Look for errors (red text)

3. **Check Function Logs:**
   - Open a deployment
   - Click "Functions" tab
   - Click on a function
   - View "Logs" section

4. **Check Environment Variables:**
   - Go to Project Settings
   - Click "Environment Variables"
   - Verify all required vars are set

## API Endpoints Used

The script uses these Vercel API endpoints:

- `GET /v9/projects` - List projects
- `GET /v13/deployments/{id}` - Get deployment details
- `GET /v2/deployments/{id}/events` - Get build events
- `GET /v1/deployments/{id}/logs` - Get function logs

## Troubleshooting

### Script fails with "401 Unauthorized"

**Cause:** Invalid or expired token

**Fix:**
- Generate a new token
- Make sure token has correct permissions

### Script fails with "404 Not Found"

**Cause:** Project doesn't exist or wrong name

**Fix:**
- List all projects to see correct name
- Check project name spelling

### No deployments shown

**Cause:** No deployments yet or project not deployed

**Fix:**
- Push to GitHub to trigger deployment
- Or deploy manually via Vercel dashboard

## Next Steps

After running diagnostics:

1. **If deployment is ERROR:**
   - Check build logs for specific error
   - Fix the issue in code
   - Push to trigger new deployment

2. **If function is failing:**
   - Check function logs
   - Verify function code
   - Check environment variables

3. **If everything is READY:**
   - Visit the deployment URL
   - Test the application
   - Check browser console for client-side errors

## Integration with Error Logging

The diagnostic script works alongside the error logging system:

1. **Server-side errors** → Check Vercel function logs
2. **Client-side errors** → Check `/error-logs` page
3. **Build errors** → Check deployment build logs

Use both for comprehensive error tracking!

