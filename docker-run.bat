@echo off
REM Docker wrapper script for Windows users
REM Batocera Arcade Downloader

setlocal enabledelayedexpansion

set IMAGE_NAME=arcade-downloader:latest
set DATA_DIR=%cd%\data

REM Create data directory if it doesn't exist
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed
    echo Please install Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
    exit /b 1
)

REM Check if image exists, build if not
docker image inspect %IMAGE_NAME% >nul 2>&1
if errorlevel 1 (
    echo Image not found. Building...
    call :build_image
)

REM Parse command
if "%1"=="" goto show_usage
if "%1"=="build" goto build_image
if "%1"=="interactive" goto run_interactive
if "%1"=="help" goto show_usage
if "%1"=="--help" goto show_usage
if "%1"=="-h" goto show_usage
if "%1"=="shell" goto run_shell

REM Default: run CLI command
goto run_cli

:build_image
echo Building Docker image...
docker build -t %IMAGE_NAME% .
echo Image built successfully
exit /b 0

:run_interactive
echo Starting interactive mode...
docker run -it --rm --network host -v "%DATA_DIR%:/data" %IMAGE_NAME% interactive.py
exit /b 0

:run_cli
docker run -it --rm --network host -v "%DATA_DIR%:/data" %IMAGE_NAME% arcade_downloader.py %*
exit /b 0

:run_shell
echo Opening shell in container...
docker run -it --rm --network host -v "%DATA_DIR%:/data" --entrypoint /bin/bash %IMAGE_NAME%
exit /b 0

:show_usage
echo.
echo Batocera Arcade Downloader - Docker Wrapper (Windows)
echo.
echo Usage:
echo   %~nx0 [command] [options]
echo.
echo Commands:
echo   build                  Build the Docker image
echo   interactive            Run in interactive menu mode
echo   search ^<query^>         Search for ROMs
echo   download               Download a ROM to Batocera
echo   queue                  Manage download queue
echo   list-systems           List systems on Batocera
echo   browse ^<identifier^>    Browse archive.org item
echo   shell                  Open shell in container
echo   help                   Show this help
echo.
echo Examples:
echo   %~nx0 build
echo   %~nx0 interactive
echo   %~nx0 search "street fighter" --host 192.168.1.100
echo   %~nx0 download --url "https://archive.org/..." --system mame --host 192.168.1.100
echo   %~nx0 queue add --url "URL" --system mame
echo   %~nx0 queue process --host 192.168.1.100
echo.
exit /b 0
