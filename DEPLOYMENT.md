# Deployment Guide

This guide covers deploying the Dental Clinic Trawler application.

> **Note**: For Vercel deployment, see [dentaltrawler/VERCEL_DEPLOY.md](dentaltrawler/VERCEL_DEPLOY.md)

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (for containerized deployment)
- Google Places API key (optional, for enhanced data)

## Local Development

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
# Edit .env and add your GOOGLE_PLACES_API_KEY
```

### 3. Run the Scraper

```bash
# Using the enhanced trawler
python enhanced_trawler.py

# Or using the original trawler
python dental_trawler.py
```

### 4. Start the API Server

```bash
python run_api.py
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Search Interface: `http://localhost:8000/`
- Dashboard: `http://localhost:8000/dashboard.html`

## Docker Deployment

### 1. Build and Run with Docker Compose

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Build Docker Image Manually

```bash
# Build image
docker build -t dental-trawler .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e GOOGLE_PLACES_API_KEY=your_key_here \
  dental-trawler
```

## Scheduled Updates

### Using the Scheduler Script

```bash
# Run scheduler (runs daily at 2 AM)
python scheduler.py
```

### Using Cron (Linux/Mac)

Add to crontab:

```bash
crontab -e
```

Add this line to run daily at 2 AM:

```
0 2 * * * cd /path/to/project && /usr/bin/python3 scheduler.py >> /path/to/logs/scheduler.log 2>&1
```

### Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to "Daily" at 2:00 AM
4. Set action to run: `python scheduler.py`
5. Set working directory to project folder

## Cloud Deployment

### Heroku

1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: python run_api.py
   worker: python scheduler.py
   ```
3. Deploy:
   ```bash
   heroku create dental-trawler
   heroku config:set GOOGLE_PLACES_API_KEY=your_key
   git push heroku main
   ```

### AWS Elastic Beanstalk

1. Install EB CLI
2. Initialize:
   ```bash
   eb init
   eb create dental-trawler-env
   ```
3. Set environment variables in AWS Console
4. Deploy:
   ```bash
   eb deploy
   ```

### Google Cloud Run

1. Build and push image:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/dental-trawler
   ```
2. Deploy:
   ```bash
   gcloud run deploy dental-trawler \
     --image gcr.io/PROJECT_ID/dental-trawler \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### Azure App Service

1. Install Azure CLI
2. Create app service:
   ```bash
   az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name dental-trawler
   ```
3. Deploy:
   ```bash
   az webapp deployment source config-zip --resource-group myResourceGroup --name dental-trawler --src app.zip
   ```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GOOGLE_PLACES_API_KEY` | Google Places API key | No | - |
| `PORT` | Server port | No | 8000 |
| `HOST` | Server host | No | 0.0.0.0 |

## API Endpoints

- `GET /` - Search interface
- `GET /api/health` - Health check
- `GET /api/metadata` - Data freshness metadata
- `GET /api/clinics` - List all clinics
- `POST /api/search` - Search clinics with filters
- `GET /api/statistics` - Get statistics
- `GET /api/services` - List all services
- `GET /api/languages` - List all languages

## Monitoring

### Health Checks

The API includes a health endpoint:

```bash
curl http://localhost:8000/api/health
```

### Logs

Logs are output to stdout/stderr. For production, consider:

- Using a logging service (e.g., Loggly, Papertrail)
- Setting up log rotation
- Monitoring with tools like Prometheus + Grafana

## Troubleshooting

### API not starting

- Check if port 8000 is available
- Verify all dependencies are installed
- Check logs for errors

### Scraper not finding data

- Verify network connectivity
- Check if target websites are accessible
- Review rate limiting settings in `config.py`

### Google Places API errors

- Verify API key is correct
- Check API quota/billing
- Ensure Places API is enabled in Google Cloud Console

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Rate Limiting**: Implement rate limiting for production
3. **CORS**: Configure CORS appropriately for your domain
4. **HTTPS**: Use HTTPS in production
5. **Authentication**: Consider adding authentication for admin endpoints

## Scaling

For high-traffic deployments:

1. Use a reverse proxy (nginx, Traefik)
2. Implement caching (Redis)
3. Use a database instead of JSON files
4. Set up load balancing
5. Use a message queue for scraping jobs

