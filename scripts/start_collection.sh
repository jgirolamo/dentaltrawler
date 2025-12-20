#!/bin/bash
# Start continuous clinic collection in the background

cd "$(dirname "$0")/.." || exit 1

echo "🚀 Starting London Zone 1 & 2 clinic collection..."
echo "   Target: 500 clinics"
echo "   Interval: Every 3 hours"
echo "   Log file: collection.log"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Start in background
nohup python3 scripts/collect_central_london_clinics.py --continuous > collection.log 2>&1 &

# Get the process ID
PID=$!

echo "✅ Collection started (PID: $PID)"
echo "📋 To view logs: tail -f collection.log"
echo "🛑 To stop: kill $PID"
echo ""
echo "Check progress: cat data/collection_state.json"

