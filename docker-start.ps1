# PowerShell script to help users run the containerized application

# Check if .env file exists, if not, create from example
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file from .env.example..."
    Copy-Item startup_agent/.env.example .env
    Write-Host "Please edit the .env file to add your API keys before continuing."
    exit 1
}

# Check for Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker not found. Please install Docker Desktop."
    exit 1
}

# Display menu
Write-Host "==== Venture Watch Docker Menu ===="
Write-Host "1. Run full stack (agent, dashboard, and scheduler)"
Write-Host "2. Run dashboard only"
Write-Host "3. Run one-time data collection"
Write-Host "4. Stop all services"
Write-Host "5. View logs"
Write-Host "0. Exit"
Write-Host "=================================="

# Get user input
$choice = Read-Host "Enter your choice"

switch ($choice) {
    1 {
        Write-Host "Starting all services..."
        docker-compose up -d
        Write-Host "Services started! Dashboard available at http://localhost:8501"
    }
    2 {
        Write-Host "Starting dashboard only..."
        docker-compose up -d dashboard
        Write-Host "Dashboard started! Available at http://localhost:8501"
    }
    3 {
        Write-Host "Running one-time data collection..."
        docker-compose run --rm agent
        Write-Host "Data collection complete!"
    }
    4 {
        Write-Host "Stopping all services..."
        docker-compose down
        Write-Host "All services stopped!"
    }
    5 {
        Write-Host "Showing logs (press Ctrl+C to exit)..."
        docker-compose logs -f
    }
    0 {
        Write-Host "Exiting..."
        exit 0
    }
    default {
        Write-Host "Invalid choice!"
    }
} 