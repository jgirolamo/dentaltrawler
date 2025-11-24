# Dental Trawler Frontend

React + Vite frontend for the Dental Clinic Search application.

## Development

```bash
# Install dependencies
npm install

# Start dev server (runs on http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create a `.env` file (see `.env.example`) to configure the API URL:

```
VITE_API_URL=http://localhost:8000
```

## Features

- **Search Page** (`/`) - Advanced clinic search with filters
- **Dashboard** (`/dashboard`) - Statistics and overview of all clinics

## API Integration

The frontend connects to the FastAPI backend running on port 8000. Make sure the API server is running before using the frontend.

## Deployment

### Vercel (Recommended)

See [VERCEL_DEPLOY.md](./VERCEL_DEPLOY.md) for detailed deployment instructions.

Quick deploy:
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in this directory
3. Set `VITE_API_URL` environment variable
4. Deploy: `vercel --prod`

### Other Platforms

The built `dist` folder can be deployed to any static hosting service:
- Netlify
- GitHub Pages
- Cloudflare Pages
- AWS S3 + CloudFront
