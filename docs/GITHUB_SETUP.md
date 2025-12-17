# GitHub Setup for Vercel Deployment

This guide helps you set up your repository for automatic Vercel deployment from GitHub.

## Step 1: Create GitHub Repository

1. Go to [github.com](https://github.com) and sign in
2. Click the "+" icon → "New repository"
3. Name your repository (e.g., `dental-clinic-search`)
4. Choose Public or Private
5. **Don't** initialize with README (if you already have files)
6. Click "Create repository"

## Step 2: Push Your Code to GitHub

From your project root directory:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Dental Clinic Search app"

# Add GitHub remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Vercel from GitHub

1. **Go to Vercel**: [vercel.com](https://vercel.com)
2. **Sign in** with GitHub (recommended) or create account
3. **Click "Add New Project"**
4. **Import Git Repository**:
   - You'll see your GitHub repositories
   - Click "Import" next to your repository
5. **Configure Project**:
   - **Root Directory**: Click "Edit" → Enter `dentaltrawler`
   - **Framework Preset**: Vite (should auto-detect)
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)
6. **Environment Variables**:
   - Click "Environment Variables"
   - Add: `VITE_API_URL` = `https://your-backend-api-url.com`
7. **Deploy**: Click "Deploy"

## Step 4: Automatic Deployments

After the first deployment, Vercel will automatically:
- ✅ Deploy on every push to `main` branch
- ✅ Create preview deployments for pull requests
- ✅ Show build status in GitHub

## Repository Structure

Your GitHub repo should look like this:

```
your-repo/
├── dentaltrawler/          # Frontend (Vite + React)
│   ├── src/
│   ├── package.json
│   ├── vercel.json
│   └── ...
├── api.py                  # Backend API
├── requirements.txt
├── dental_trawler.py
├── enhanced_trawler.py
└── README.md
```

## Important Files for GitHub

Make sure these are in your repository:
- ✅ `dentaltrawler/vercel.json` - Vercel configuration
- ✅ `dentaltrawler/package.json` - Dependencies
- ✅ `.gitignore` - Excludes node_modules, .env, etc.

## Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

- `VITE_API_URL` - Your backend API URL

## Troubleshooting

### Build fails: "Cannot find module"
- Make sure `dentaltrawler/package.json` has all dependencies
- Check that Root Directory is set to `dentaltrawler`

### Build fails: "Command not found"
- Vercel uses Node.js 18+ by default
- Check build logs in Vercel dashboard

### API calls fail
- Verify `VITE_API_URL` is set correctly
- Check CORS settings in your backend API
- Ensure backend is deployed and accessible

## Next Steps

1. Deploy backend to Render/Railway (see main README)
2. Update `VITE_API_URL` in Vercel with backend URL
3. Your app is live! 🎉

## Benefits of GitHub Integration

- ✅ Automatic deployments on every push
- ✅ Preview deployments for PRs
- ✅ Build status in GitHub
- ✅ Easy rollback to previous versions
- ✅ Team collaboration

