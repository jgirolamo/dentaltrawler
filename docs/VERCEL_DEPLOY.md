# Deploying to Vercel

This guide will help you deploy the Dental Clinic Search frontend to Vercel.

## Prerequisites

1. A Vercel account (sign up at [vercel.com](https://vercel.com))
2. Your API backend hosted somewhere (Render, Railway, etc.)
3. GitHub account (recommended for easy deployment)

## Step 1: Prepare Your Code

1. Make sure your `dentaltrawler` folder has all the latest changes
2. Commit your code to a GitHub repository

## Step 2: Deploy Frontend to Vercel (GitHub Integration)

### Recommended: Deploy via GitHub (Automatic)

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com) and sign in
   - Click "Add New Project"
   - Click "Import Git Repository"
   - Select your GitHub repository
   - Click "Import"

3. **Configure Project Settings**:
   - **Framework Preset**: Vite (auto-detected)
   - **Root Directory**: `dentaltrawler` (click "Edit" and set this)
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

4. **Add Environment Variable**:
   - Click "Environment Variables"
   - Add:
     - **Name**: `VITE_API_URL`
     - **Value**: Your backend API URL (e.g., `https://your-api.onrender.com`)
     - **Environment**: Production, Preview, Development (select all)

5. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete (~2-3 minutes)
   - Your app will be live at `https://your-project.vercel.app`

### Automatic Deployments

Once connected to GitHub:
- **Every push to `main` branch** → Production deployment
- **Every pull request** → Preview deployment
- **Automatic** → No manual steps needed!

### Option B: Deploy via Vercel CLI (Alternative)

### Option B: Deploy via Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Navigate to the frontend directory:
   ```bash
   cd dentaltrawler
   ```

3. Login to Vercel:
   ```bash
   vercel login
   ```

4. Deploy:
   ```bash
   vercel
   ```

5. Set environment variable:
   ```bash
   vercel env add VITE_API_URL
   # Enter your API URL when prompted
   ```

6. Redeploy with environment variable:
   ```bash
   vercel --prod
   ```

## Step 3: Update API URL

After deployment, update the `vercel.json` file with your actual API URL:

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://YOUR-ACTUAL-API-URL.com/api/$1"
    }
  ]
}
```

Or set the `VITE_API_URL` environment variable in Vercel dashboard.

## Step 4: Deploy Backend (Separate Service)

Your FastAPI backend needs to be hosted separately. Recommended options:

### Render.com (Free Tier)

1. Create account at [render.com](https://render.com)
2. Create new "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run_api.py`
   - **Environment Variables**:
     - `PORT` (auto-provided by Render)
     - `GOOGLE_PLACES_API_KEY` (if using)

5. Deploy and copy the URL (e.g., `https://dental-api.onrender.com`)

### Railway.app

1. Create account at [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select your repo
4. Railway will auto-detect Python
5. Set environment variables
6. Deploy

## Step 5: Update Frontend API URL

Once your backend is deployed:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Update `VITE_API_URL` with your backend URL
3. Redeploy (or wait for automatic redeploy)

## Custom Domain (Optional)

1. In Vercel Dashboard → Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

## Environment Variables

### Frontend (Vercel)
- `VITE_API_URL` - Your backend API URL

### Backend (Render/Railway)
- `PORT` - Server port (usually auto-set)
- `GOOGLE_PLACES_API_KEY` - Optional, for Google Places integration

## Troubleshooting

### Frontend can't connect to API
- Check `VITE_API_URL` is set correctly
- Ensure backend CORS allows your Vercel domain
- Check backend is running and accessible

### Build fails
- Check Node.js version (Vercel uses Node 18+ by default)
- Ensure all dependencies are in `package.json`
- Check build logs in Vercel dashboard

### API returns CORS errors
- Update `api.py` to allow your Vercel domain:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["https://your-app.vercel.app", "http://localhost:5173"],
      ...
  )
  ```

## Continuous Deployment

Vercel automatically deploys when you push to your main branch. Each push creates a new preview deployment.

## Support

- Vercel Docs: https://vercel.com/docs
- Vercel Discord: https://vercel.com/discord

