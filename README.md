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
- Python 3.7 or higher
- SSH access to your Batocera cabinet (enabled by default)
- Network connectivity to your Batocera cabinet

### Setup

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

## Legal Notice

This tool is provided for downloading legally obtained ROM files only. Users are responsible for ensuring they have the legal right to download and use any ROMs. Many arcade games are still under copyright protection.

Public domain and freely distributed ROMs can be found in various archive.org collections.

## License

MIT License - Feel free to modify and distribute as needed.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
