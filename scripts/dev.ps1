# CodeToQuery Development Script (Windows)

cd backend

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Start the development server
Write-Host "🚀 Starting CodeToQuery Backend..." -ForegroundColor Green
Write-Host "API documentation: http://localhost:8000/api/v1/docs" -ForegroundColor Cyan
Write-Host ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
