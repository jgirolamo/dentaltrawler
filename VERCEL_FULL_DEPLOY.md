# Full Deployment Guide: Frontend + Backend on Vercel

This guide covers deploying both the React frontend and FastAPI backend to Vercel.

## Architecture

- **Frontend**: Vite + React → Vercel (Static Site)
- **Backend**: FastAPI → Vercel (Serverless Functions)

## Option 1: Separate Projects (Recommended)

### Frontend on Vercel

1. Go to [vercel.com](https://vercel.com)
2. Import `jgirolamo/dentaltrawler` repository
3. Set **Root Directory**: `dentaltrawler`
4. Framework: Vite (auto-detected)
5. Add environment variable: `VITE_API_URL` = your backend URL

### Backend on Render/Railway (Recommended for Python)

Since Vercel's Python runtime has limitations for full FastAPI apps, deploy backend separately:

#### Render.com (Free Tier)

1. Create account at [render.com](https://render.com)
2. New → Web Service
3. Connect GitHub repo: `jgirolamo/dentaltrawler`
4. Configure:
   - **Name**: `dental-api`
   - **Root Directory**: `/` (root)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run_api.py`
5. Environment Variables:
   - `PORT` (auto-provided)
   - `GOOGLE_PLACES_API_KEY` (optional)
6. Deploy → Copy URL (e.g., `https://dental-api.onrender.com`)

7. Update frontend `VITE_API_URL` in Vercel with this URL

## Option 2: Both on Vercel (Serverless Functions)

Vercel supports Python serverless functions, but requires restructuring:

### Setup Backend as Vercel Functions

1. Create `api/` directory in root
2. Move `api.py` to `api/index.py`
3. Adapt for serverless (see below)

### Limitations:
- File system is read-only (except `/tmp`)
- Need to upload JSON files or use external storage
- Cold starts on first request
- 10-second timeout on Hobby plan

## Recommended: Hybrid Approach

**Frontend**: Vercel (fast, free, perfect for React)
**Backend**: Render/Railway (better for Python, file I/O, long-running)

This gives you:
- ✅ Fast frontend CDN
- ✅ Reliable backend with file access
- ✅ Free tier on both
- ✅ Automatic deployments

## Quick Deploy Commands

### Frontend (Vercel)
```bash
cd dentaltrawler
vercel --prod
```

### Backend (Render)
- Use Render dashboard (no CLI needed)
- Or use Railway CLI:
```bash
railway login
railway init
railway up
```

## Environment Variables

### Frontend (Vercel)
- `VITE_API_URL` = `https://your-backend.onrender.com`

### Backend (Render/Railway)
- `PORT` = auto-set
- `GOOGLE_PLACES_API_KEY` = optional

## Data Files

For production, consider:
1. **Upload JSON to cloud storage** (S3, Cloudinary)
2. **Use a database** (PostgreSQL, MongoDB)
3. **Keep in repo** (if small, < 1MB)

Current setup uses local JSON files which work on Render/Railway but not on Vercel serverless.

