# CodeToQuery Backend Setup Script (Windows)

Write-Host "🚀 Setting up CodeToQuery Backend..." -ForegroundColor Green

# Check Python version
Write-Host "📋 Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version
Write-Host "Python version: $pythonVersion"

# Create virtual environment
Write-Host "🔧 Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "✅ Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
cd backend
pip install -r requirements.txt

# Copy environment file
Write-Host "📝 Creating environment file..." -ForegroundColor Yellow
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "⚠️  Please edit .env with your configuration" -ForegroundColor Red
}

# Create database
Write-Host "🗄️  Creating database..." -ForegroundColor Yellow
try {
    createdb codetoquery
} catch {
    Write-Host "Database already exists" -ForegroundColor Yellow
}

# Run migrations
Write-Host "🔄 Running database migrations..." -ForegroundColor Yellow
alembic upgrade head

Write-Host "✨ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the development server:" -ForegroundColor Cyan
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  uvicorn app.main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "API documentation will be available at: http://localhost:8000/api/v1/docs" -ForegroundColor Cyan
