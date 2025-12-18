# Dental Trawler - London Dental Clinic Search

A modern web application for searching and discovering private dental clinics in London, UK.

## 🚀 Features

- **Real Clinic Data**: 48+ verified dental clinics from OpenStreetMap
- **Advanced Search**: Filter by services, languages, area, postcode, and more
- **Interactive Dashboard**: Statistics and visualizations
- **Error Logging**: Comprehensive error tracking and monitoring
- **Responsive Design**: Works on desktop and mobile devices

## 📋 Quick Start

### Prerequisites

- Node.js 20+ and npm
- Python 3.8+ (for data collection scripts)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jgirolamo/dentaltrawler.git
   cd dentaltrawler
   ```

2. **Install frontend dependencies:**
   ```bash
   cd dentaltrawler
   npm install
   ```

3. **Run locally:**
   ```bash
   npm run dev
   ```

4. **Open in browser:**
   ```
   http://localhost:5173
   ```

## 📁 Project Structure

```
dentaltrawler/
├── src/              # React frontend source
├── public/           # Static assets
├── dist/             # Build output
scripts/              # Data collection scripts
├── data/             # Data files (JSON, CSV)
├── docs/             # Documentation
└── api/              # Vercel serverless functions
```

## 🔧 Data Sources

Currently using **OpenStreetMap** (free, no API key required) for real dental clinic data.

To get more data:
- **Google Places API**: Best quality (requires API key)
- **Yelp Fusion API**: Great reviews (requires API key)
- **OpenStreetMap**: Free, open-source (already implemented)

See `docs/` for detailed guides on data sources.

## 🚀 Deployment

The app is configured for **Vercel** deployment:

1. Push to GitHub
2. Connect repository to Vercel
3. Deploy automatically

See `docs/DEPLOYMENT.md` for detailed instructions.

## 📚 Documentation

All documentation is in the `docs/` directory:

- **Getting Started**: `docs/README.md`
- **Data Sources**: `docs/GET_REAL_DATA.md`, `ALTERNATIVE_APIS.md`
- **Deployment**: `docs/DEPLOYMENT.md`, `docs/VERCEL_DEPLOY.md`
- **Error Logging**: `ERROR_LOGGING.md`, `HOW_TO_ACCESS_LOGS.md`
- **Project Structure**: `docs/PROJECT_STRUCTURE.md`

## 🛠️ Development

### Frontend
```bash
cd dentaltrawler
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview production build
```

### Data Collection
```bash
# Get real data from OpenStreetMap (free)
python3 scripts/fetch_openstreetmap.py London 50

# Or use other sources (see scripts/README.md)
```

## 📊 Current Status

- ✅ **48 real dental clinics** from OpenStreetMap
- ✅ **Frontend**: React + Vite
- ✅ **Deployment**: Vercel
- ✅ **Error Logging**: Comprehensive system
- ✅ **Search**: Advanced filtering and pagination

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🔗 Links

- **Live App**: [Vercel Deployment]
- **Error Logs**: `/error-logs` (in app)
- **HTML Directory**: `/clinics.html` (in app)

---

For detailed documentation, see the `docs/` directory.
