@echo off
REM Windows batch file to help users run the containerized application

REM Check if .env file exists, if not, create from example
IF NOT EXIST .env (
    echo Creating .env file from .env.example...
    copy startup_agent\.env.example .env
    echo Please edit the .env file to add your API keys before continuing.
    exit /b 1
)

REM Check for Docker
docker --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Docker not found. Please install Docker Desktop.
    exit /b 1
)

:MENU
echo ==== Venture Watch Docker Menu ====
echo 1. Run full stack (agent, dashboard, and scheduler)
echo 2. Run dashboard only
echo 3. Run one-time data collection
echo 4. Stop all services
echo 5. View logs
echo 0. Exit
echo ==================================

set /p choice=Enter your choice: 

if "%choice%"=="1" (
    echo Starting all services...
    docker-compose up -d
    echo Services started! Dashboard available at http://localhost:8501
    goto END
)

if "%choice%"=="2" (
    echo Starting dashboard only...
    docker-compose up -d dashboard
    echo Dashboard started! Available at http://localhost:8501
    goto END
)

if "%choice%"=="3" (
    echo Running one-time data collection...
    docker-compose run --rm agent
    echo Data collection complete!
    goto END
)

if "%choice%"=="4" (
    echo Stopping all services...
    docker-compose down
    echo All services stopped!
    goto END
)

if "%choice%"=="5" (
    echo Showing logs (press Ctrl+C to exit)...
    docker-compose logs -f
    goto END
)

if "%choice%"=="0" (
    echo Exiting...
    exit /b 0
)

echo Invalid choice!
goto MENU

:END
exit /b 0 