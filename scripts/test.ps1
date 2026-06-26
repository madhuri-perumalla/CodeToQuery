# CodeToQuery Test Script (Windows)

cd backend

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Run tests
Write-Host "🧪 Running tests..." -ForegroundColor Green
pytest $args

Write-Host "✅ Tests completed!" -ForegroundColor Green
