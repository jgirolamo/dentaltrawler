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

## Features

- **Search Page** (`/`) - Advanced clinic search with filters
- **Dashboard** (`/dashboard`) - Statistics and overview of all clinics

## Data

The app uses embedded clinic data from `src/clinics.js`. No backend server is required.

## Deployment

### Vercel (Recommended)

See [VERCEL_DEPLOY.md](./VERCEL_DEPLOY.md) for detailed deployment instructions.

Quick deploy:
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in this directory
3. Deploy: `vercel --prod`

### Other Platforms

The built `dist` folder can be deployed to any static hosting service:
- Netlify
- GitHub Pages
- Cloudflare Pages
- AWS S3 + CloudFront
