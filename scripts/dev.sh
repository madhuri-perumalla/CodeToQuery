#!/bin/bash

# CodeToQuery Development Script

set -e

cd backend

# Activate virtual environment
source venv/bin/activate

# Start the development server
echo "🚀 Starting CodeToQuery Backend..."
echo "API documentation: http://localhost:8000/api/v1/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
