#!/bin/bash
# filepath: ./start.sh
# Starts Flask and Huey services in the background (Linux version)

set -e

echo "Starting Flask and Huey services..."

# UV Environment Setup
uv sync --frozen

# Set environment variables for Flask
export FLASK_APP=app/app.py
export FLASK_DEBUG=1


nohup uv run flask run --no-debugger --no-reload &> flask.log  & echo "$!" > app-pid
nohup uv run huey_consumer huey_config.huey --workers=2 --verbose &> huey.log & echo "$!" > huey-pid

# Open browser depending on OS
if [[ "$(uname)" == "Darwin" ]]; then
    open http://127.0.0.1:5000/ &> /dev/null || echo "Could not open browser automatically."
else
    xdg-open http://127.0.0.1:5000/ &> /dev/null || echo "Could not open browser automatically."
fi

echo "Open http://127.0.1:5000/ in your browser to access the application."
echo "Both services started in background. Logs: flask.log, huey.log"
echo "Use ./stop.sh to stop them."
