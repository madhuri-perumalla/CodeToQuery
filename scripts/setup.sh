#!/bin/bash

# CodeToQuery Backend Setup Script

set -e

echo "🚀 Setting up CodeToQuery Backend..."

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
cd backend
pip install -r requirements.txt

# Copy environment file
echo "📝 Creating environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
fi

# Create database
echo "🗄️  Creating database..."
createdb codetoquery 2>/dev/null || echo "Database already exists"

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

echo "✨ Setup complete!"
echo ""
echo "To start the development server:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "API documentation will be available at: http://localhost:8000/api/v1/docs"
