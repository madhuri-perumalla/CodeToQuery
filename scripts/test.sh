#!/bin/bash

# CodeToQuery Test Script

set -e

cd backend

# Activate virtual environment
source venv/bin/activate

# Run tests
echo "🧪 Running tests..."
pytest "$@"

echo "✅ Tests completed!"
