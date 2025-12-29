# Batocera Arcade Game Downloader

A Python tool to remotely manage and download arcade ROMs to your Batocera cabinet over the local network. Supports searching and downloading from archive.org.

## Features

### Core Features
- ✅ Run from any computer on your local network
- ✅ Connect to Batocera arcade cabinet via SSH
- ✅ Download ROMs from URLs directly to your cabinet
- ✅ Transfer files via SCP with progress indicators

### Advanced Features
- 🔍 Search archive.org for arcade ROMs
- 📋 Browse available files in archive.org collections
- 📦 Queue multiple downloads
- 🗂️ Automatic organization by emulator system
- ⚡ Direct download to Batocera (faster) or local download + transfer

## Installation

### Prerequisites
- **Option 1 (Docker):** Docker installed on your system
- **Option 2 (Native Python):** Python 3.7 or higher
- SSH access to your Batocera cabinet (enabled by default)
- Network connectivity to your Batocera cabinet

### Quick Start with Docker (Recommended)

Docker provides the easiest way to run the tool with all dependencies included:

**Linux/Mac:**
```bash
# Clone the repository
git clone <repository-url>
cd arcade

# Run interactive mode
./docker-run.sh interactive

# Or use CLI mode
./docker-run.sh search "street fighter" --host 192.168.1.100
```

**Windows:**
```batch
REM Clone the repository
git clone <repository-url>
cd arcade

REM Run interactive mode
docker-run.bat interactive

REM Or use CLI mode
docker-run.bat search "street fighter" --host 192.168.1.100
```

The Docker wrapper scripts will automatically:
- Build the Docker image on first run
- Handle volume mounts for persistent data
- Set up networking for SSH connections

### Native Python Setup

If you prefer to run without Docker:

1. Clone or download this repository:
```bash
git clone <repository-url>
cd arcade
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Make the script executable (optional):
```bash
chmod +x arcade_downloader.py
```

## Usage

### Interactive Mode (Recommended for Beginners)

For a user-friendly menu-driven experience:
```bash
python interactive.py
```

This will launch an interactive menu where you can:
- Setup your Batocera connection
- Search for ROMs with a guided interface
- Browse and select files to download
- Manage your download queue
- View available systems

### Command-Line Mode (Advanced Users)

For automation and scripting, use the command-line interface:

### Basic Commands

#### Search for ROMs on archive.org
```bash
python arcade_downloader.py search "street fighter"
python arcade_downloader.py search "metal slug" --max-results 10
```

#### Browse files in a specific item
```bash
python arcade_downloader.py browse "MAME_0.139_ROMS_(arcade_only)"
```

#### Download a ROM directly to Batocera
```bash
python arcade_downloader.py download \
  --url "https://archive.org/download/item/game.zip" \
  --system mame \
  --host 192.168.1.100
```

#### List available systems on your Batocera
```bash
python arcade_downloader.py list-systems --host 192.168.1.100
```

### Queue Management

#### Add ROMs to download queue
```bash
python arcade_downloader.py queue add \
  --url "https://archive.org/download/item/game1.zip" \
  --system mame

python arcade_downloader.py queue add \
  --url "https://archive.org/download/item/game2.zip" \
  --system fba
```

#### List queued downloads
```bash
python arcade_downloader.py queue list
```

#### Process the entire queue
```bash
python arcade_downloader.py queue process --host 192.168.1.100
```

#### Clear completed downloads from queue
```bash
python arcade_downloader.py queue clear
```

### Docker Commands

If using Docker, simply replace `python arcade_downloader.py` with `./docker-run.sh` (Linux/Mac) or `docker-run.bat` (Windows):

**Linux/Mac:**
```bash
# Interactive mode
./docker-run.sh interactive

# Search
./docker-run.sh search "street fighter" --host 192.168.1.100

# Download
./docker-run.sh download \
  --url "https://archive.org/download/item/game.zip" \
  --system mame \
  --host 192.168.1.100

# Queue management
./docker-run.sh queue add --url "URL" --system mame
./docker-run.sh queue list
./docker-run.sh queue process --host 192.168.1.100

# List systems
./docker-run.sh list-systems --host 192.168.1.100

# Open shell in container for debugging
./docker-run.sh shell
```

**Windows:**
```batch
REM Interactive mode
docker-run.bat interactive

REM Search
docker-run.bat search "street fighter" --host 192.168.1.100

REM Queue management
docker-run.bat queue add --url "URL" --system mame
docker-run.bat queue process --host 192.168.1.100
```

**Using docker-compose:**
```bash
# Interactive mode
docker-compose run --rm arcade-downloader interactive.py

# CLI commands
docker-compose run --rm arcade-downloader \
  arcade_downloader.py search "game name" --host 192.168.1.100
```

## Configuration

### Batocera Connection Settings

Default Batocera SSH credentials:
- **Username:** `root`
- **Password:** `linux`
- **Port:** `22`

You can override these with command-line arguments:
```bash
python arcade_downloader.py download \
  --host 192.168.1.100 \
  --username root \
  --password mypassword \
  --port 22 \
  --url "..." \
  --system mame
```

### Supported Systems

Common arcade systems in Batocera:
- `mame` - MAME (Multiple Arcade Machine Emulator)
- `fba` or `fbneo` - FinalBurn Alpha/Neo
- `arcade` - General arcade directory
- `neogeo` - Neo Geo
- `cps1`, `cps2`, `cps3` - Capcom Play System

To see what systems are available on your specific Batocera installation:
```bash
python arcade_downloader.py list-systems --host 192.168.1.100
```

## Archive.org Collections

The tool searches these popular arcade ROM collections by default:
- MAME_0.139_ROMS_(arcade_only)
- MAME_0.37b5_ROMs_(MAME_2000)
- MAME_2003_Reference_Set_MAME_0.78_ROMs
- MAME_0.151_Software_List_ROMs_(CHDs)
- FinalBurn_Neo_-_Arcade_Games

## Workflow Examples

### Example 1: Find and download a specific game
```bash
# 1. Search for the game
python arcade_downloader.py search "metal slug"

# 2. Browse the files in the collection
python arcade_downloader.py browse "MAME_0.139_ROMS_(arcade_only)"

# 3. Download directly to Batocera
python arcade_downloader.py download \
  --url "https://archive.org/download/MAME_0.139_ROMS_(arcade_only)/mslug.zip" \
  --system mame \
  --host 192.168.1.100
```

### Example 2: Queue multiple games for batch download
```bash
# Add multiple games to queue
python arcade_downloader.py queue add \
  --url "https://archive.org/download/.../game1.zip" \
  --system mame

python arcade_downloader.py queue add \
  --url "https://archive.org/download/.../game2.zip" \
  --system mame

python arcade_downloader.py queue add \
  --url "https://archive.org/download/.../game3.zip" \
  --system neogeo

# Review the queue
python arcade_downloader.py queue list

# Process all downloads
python arcade_downloader.py queue process --host 192.168.1.100

# Clean up completed items
python arcade_downloader.py queue clear
```

## Tips and Tricks

### Finding Your Batocera IP Address
On your Batocera cabinet:
1. Press F1 to open the menu
2. Go to "Network Settings"
3. Your IP address will be displayed

Or from another computer on the same network:
```bash
# Scan your network for Batocera
nmap -sn 192.168.1.0/24 | grep -B 2 "batocera"
```

### Direct Download vs Local Transfer
- **Direct download** (default): Batocera downloads the file itself. Faster and saves bandwidth on your computer.
- **Local transfer** (`--local` flag): Download to your computer first, then transfer. Useful if Batocera has limited internet access.

### ROM Organization
The script automatically creates system directories if they don't exist. ROMs are organized as:
```
/userdata/roms/
├── mame/
│   ├── game1.zip
│   └── game2.zip
├── neogeo/
│   └── game3.zip
└── fba/
    └── game4.zip
```

### Security Note
The default Batocera credentials (`root`/`linux`) should be changed if your cabinet is exposed to untrusted networks. You can change the password through Batocera's web interface or SSH.

## Troubleshooting

### Cannot connect to Batocera
- Verify the IP address is correct
- Ensure Batocera is on and connected to the network
- Check that SSH is enabled in Batocera settings
- Verify firewall settings

### Download fails
- Check that the URL is valid and accessible
- Ensure Batocera has internet connectivity
- Verify you have sufficient storage space on Batocera
- Try using `--local` to download via your computer instead

### ROM doesn't appear in Batocera
- Refresh the game list in EmulationStation (Start → Game Collection Settings → Update Game Lists)
- Verify the ROM is in the correct system directory
- Check that the ROM format is supported by the emulator

### Docker-specific issues

#### Image not found or build fails
```bash
# Rebuild the Docker image
./docker-run.sh build

# Or manually
docker build -t arcade-downloader:latest .
```

#### Cannot connect from Docker container
- Ensure you're using `--network host` (the wrapper scripts do this automatically)
- On Windows/Mac, Docker networking may require the actual IP instead of localhost
- Check that your firewall allows Docker network access

#### Permission errors with data directory
```bash
# Linux/Mac: Fix permissions on data directory
sudo chown -R $USER:$USER ./data

# Or run with elevated permissions if needed
sudo ./docker-run.sh interactive
```

#### Queue file not persisting
- Ensure the `./data` directory exists and is mounted correctly
- Check docker-compose.yml or wrapper script volume mounts
- The queue file should be in `./data/download_queue.json`

#### Docker commands not found (Windows)
- Ensure Docker Desktop is running
- Add Docker to your PATH environment variable
- Run `docker --version` to verify installation

## Legal Notice

This tool is provided for downloading legally obtained ROM files only. Users are responsible for ensuring they have the legal right to download and use any ROMs. Many arcade games are still under copyright protection.

Public domain and freely distributed ROMs can be found in various archive.org collections.

## License

MIT License - Feel free to modify and distribute as needed.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
