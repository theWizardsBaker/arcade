#!/bin/bash
# Quick start script for Batocera Arcade Downloader

echo "======================================"
echo "Batocera Arcade Game Downloader"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import paramiko, scp, requests, tqdm" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Check if config exists
if [ ! -f "config.json" ]; then
    echo "No config.json found. Please create one from config.example.json"
    echo "Example:"
    echo "  cp config.example.json config.json"
    echo "  nano config.json  # Edit with your Batocera IP address"
    echo ""
fi

# Display help menu
echo "Available commands:"
echo ""
echo "1. Search for ROMs:"
echo "   python3 arcade_downloader.py search \"game name\" --host YOUR_BATOCERA_IP"
echo ""
echo "2. Download a ROM:"
echo "   python3 arcade_downloader.py download --url \"URL\" --system mame --host YOUR_BATOCERA_IP"
echo ""
echo "3. Queue multiple downloads:"
echo "   python3 arcade_downloader.py queue add --url \"URL\" --system mame"
echo "   python3 arcade_downloader.py queue list"
echo "   python3 arcade_downloader.py queue process --host YOUR_BATOCERA_IP"
echo ""
echo "4. List systems on Batocera:"
echo "   python3 arcade_downloader.py list-systems --host YOUR_BATOCERA_IP"
echo ""
echo "For full documentation, see README.md"
echo ""
