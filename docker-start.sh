#!/bin/bash
# Script to help users run the containerized application

# Check if .env file exists, if not, create from example
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp startup_agent/.env.example .env
    echo "Please edit the .env file to add your API keys before continuing."
    exit 1
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker and Docker Compose."
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# Display menu
echo "==== Venture Watch Docker Menu ===="
echo "1. Run full stack (agent, dashboard, and scheduler)"
echo "2. Run dashboard only"
echo "3. Run one-time data collection"
echo "4. Stop all services"
echo "5. View logs"
echo "0. Exit"
echo "=================================="

# Get user input
read -p "Enter your choice: " choice

case $choice in
    1)
        echo "Starting all services..."
        docker-compose up -d
        echo "Services started! Dashboard available at http://localhost:8501"
        ;;
    2)
        echo "Starting dashboard only..."
        docker-compose up -d dashboard
        echo "Dashboard started! Available at http://localhost:8501"
        ;;
    3)
        echo "Running one-time data collection..."
        docker-compose run --rm agent
        echo "Data collection complete!"
        ;;
    4)
        echo "Stopping all services..."
        docker-compose down
        echo "All services stopped!"
        ;;
    5)
        echo "Showing logs (press Ctrl+C to exit)..."
        docker-compose logs -f
        ;;
    0)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice!"
        ;;
esac 