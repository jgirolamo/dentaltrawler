#!/bin/bash
# Start Dental Trawler - API and Frontend

echo "🦷 Starting Dental Trawler..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Start API server in background
echo -e "${BLUE}Starting API server on http://localhost:8000${NC}"
cd "$(dirname "$0")"
python3 api/live_search.py &
API_PID=$!

# Wait for API to start
sleep 2

# Start frontend dev server
echo -e "${GREEN}Starting frontend on http://localhost:5173${NC}"
cd dentaltrawler
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "🦷 Dental Trawler is running!"
echo ""
echo "  API:      http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "  Press Ctrl+C to stop"
echo "=========================================="

# Wait for Ctrl+C
trap "kill $API_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
