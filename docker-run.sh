#!/bin/bash
# Docker wrapper script for Batocera Arcade Downloader
# Makes it easy to run the tool in Docker without remembering complex commands

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
IMAGE_NAME="arcade-downloader:latest"
DATA_DIR="./data"

# Create data directory if it doesn't exist
mkdir -p "$DATA_DIR"

# Function to build the Docker image
build_image() {
    echo -e "${BLUE}Building Docker image...${NC}"
    docker build -t "$IMAGE_NAME" .
    echo -e "${GREEN}✓ Image built successfully${NC}"
}

# Function to run interactive mode
run_interactive() {
    echo -e "${BLUE}Starting interactive mode...${NC}"
    docker run -it --rm \
        --network host \
        -v "$(pwd)/data:/data" \
        "$IMAGE_NAME" \
        interactive.py
}

# Function to run CLI command
run_cli() {
    docker run -it --rm \
        --network host \
        -v "$(pwd)/data:/data" \
        "$IMAGE_NAME" \
        arcade_downloader.py "$@"
}

# Function to show usage
show_usage() {
    cat <<EOF
${BLUE}Batocera Arcade Downloader - Docker Wrapper${NC}

Usage:
  $0 [command] [options]

Commands:
  ${GREEN}build${NC}                  Build the Docker image
  ${GREEN}interactive${NC}            Run in interactive menu mode
  ${GREEN}search${NC} <query>         Search for ROMs
  ${GREEN}download${NC}               Download a ROM to Batocera
  ${GREEN}queue${NC}                  Manage download queue
  ${GREEN}list-systems${NC}           List systems on Batocera
  ${GREEN}browse${NC} <identifier>    Browse archive.org item
  ${GREEN}shell${NC}                  Open shell in container
  ${GREEN}help${NC}                   Show this help

Examples:
  # Build the image
  $0 build

  # Run interactive mode
  $0 interactive

  # Search for games
  $0 search "street fighter" --host 192.168.1.100

  # Download a ROM
  $0 download --url "https://archive.org/..." --system mame --host 192.168.1.100

  # Manage queue
  $0 queue add --url "URL" --system mame
  $0 queue list
  $0 queue process --host 192.168.1.100

  # List Batocera systems
  $0 list-systems --host 192.168.1.100

Environment Variables:
  ${YELLOW}BATOCERA_HOST${NC}    Default Batocera IP (optional)

EOF
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if image exists
if ! docker image inspect "$IMAGE_NAME" &> /dev/null; then
    echo -e "${YELLOW}Image not found. Building...${NC}"
    build_image
fi

# Parse command
case "${1:-help}" in
    build)
        build_image
        ;;
    interactive)
        run_interactive
        ;;
    search|download|queue|list-systems|browse)
        run_cli "$@"
        ;;
    shell)
        echo -e "${BLUE}Opening shell in container...${NC}"
        docker run -it --rm \
            --network host \
            -v "$(pwd)/data:/data" \
            --entrypoint /bin/bash \
            "$IMAGE_NAME"
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        # Pass through any other commands
        run_cli "$@"
        ;;
esac
