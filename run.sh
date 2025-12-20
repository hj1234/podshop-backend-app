#!/bin/bash
# Run Flask admin app

cd "$(dirname "$0")"

# Activate virtual environment (if it exists)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Load environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export ADMIN_TOKEN=${ADMIN_TOKEN:-change-me-in-production}
export API_BASE=${API_BASE:-http://localhost:8000}
export PORT=${PORT:-5000}

echo "Starting Flask admin app on http://0.0.0.0:${PORT}"
echo "API Base: ${API_BASE}"
flask run --host=0.0.0.0 --port=${PORT}

