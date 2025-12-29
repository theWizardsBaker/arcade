#!/usr/bin/env python3
"""
Batocera Arcade Game Downloader

A tool to remotely manage and download arcade ROMs to a Batocera cabinet
over the local network. Supports searching and downloading from archive.org.
"""

import os
import sys
import argparse
import json
import requests
from urllib.parse import urljoin, urlparse
from pathlib import Path
from typing import List, Dict, Optional
import paramiko
from scp import SCPClient
from tqdm import tqdm


class BatoceraManager:
    """Manages connection and file operations with Batocera cabinet"""

    def __init__(self, host: str, username: str = 'root', password: str = 'linux', port: int = 22):
        """
        Initialize connection to Batocera system

        Args:
            host: IP address or hostname of Batocera cabinet
            username: SSH username (default: root)
            password: SSH password (default: linux)
            port: SSH port (default: 22)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.ssh_client = None
        self.rom_base_path = '/userdata/roms'

    def connect(self):
        """Establish SSH connection to Batocera"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password
            )
            print(f"✓ Connected to Batocera at {self.host}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Batocera: {e}")
            return False

    def disconnect(self):
        """Close SSH connection"""
        if self.ssh_client:
            self.ssh_client.close()
            print("✓ Disconnected from Batocera")

    def execute_command(self, command: str) -> tuple:
        """
        Execute command on Batocera system

        Args:
            command: Shell command to execute

        Returns:
            Tuple of (stdout, stderr, exit_code)
        """
        if not self.ssh_client:
            raise ConnectionError("Not connected to Batocera")

        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        return stdout.read().decode(), stderr.read().decode(), exit_code

    def create_directory(self, system: str):
        """
        Create ROM directory for specific system if it doesn't exist

        Args:
            system: System name (e.g., 'mame', 'fba', 'arcade')
        """
        path = f"{self.rom_base_path}/{system}"
        command = f"mkdir -p {path}"
        stdout, stderr, code = self.execute_command(command)
        if code == 0:
            print(f"✓ Directory ready: {path}")
        else:
            print(f"✗ Failed to create directory: {stderr}")

    def list_systems(self) -> List[str]:
        """List available ROM systems on Batocera"""
        command = f"ls -1 {self.rom_base_path}"
        stdout, stderr, code = self.execute_command(command)
        if code == 0:
            return [s.strip() for s in stdout.split('\n') if s.strip()]
        return []

    def transfer_file(self, local_path: str, remote_path: str):
        """
        Transfer file to Batocera using SCP

        Args:
            local_path: Path to local file
            remote_path: Destination path on Batocera
        """
        if not self.ssh_client:
            raise ConnectionError("Not connected to Batocera")

        try:
            with SCPClient(self.ssh_client.get_transport(), progress=self._progress) as scp:
                scp.put(local_path, remote_path)
            print(f"\n✓ Transferred: {os.path.basename(local_path)}")
        except Exception as e:
            print(f"\n✗ Transfer failed: {e}")

    @staticmethod
    def _progress(filename, size, sent):
        """Progress callback for SCP transfers"""
        if size > 0:
            percent = (sent / size) * 100
            sys.stdout.write(f"\rTransferring: {percent:.1f}% ({sent}/{size} bytes)")
            sys.stdout.flush()

    def download_to_batocera(self, url: str, system: str, filename: Optional[str] = None):
        """
        Download file directly to Batocera (faster than local download + transfer)

        Args:
            url: URL to download from
            system: Target system directory
            filename: Optional custom filename
        """
        if not filename:
            filename = os.path.basename(urlparse(url).path)

        remote_path = f"{self.rom_base_path}/{system}/{filename}"

        # Create directory if needed
        self.create_directory(system)

        # Download directly on Batocera using wget
        command = f"wget -q --show-progress -O '{remote_path}' '{url}'"
        print(f"Downloading {filename} directly to Batocera...")

        # For direct download, we'll use a simpler approach
        command = f"wget -O '{remote_path}' '{url}' 2>&1"
        stdout, stderr, code = self.execute_command(command)

        if code == 0:
            print(f"✓ Downloaded to {remote_path}")
            return True
        else:
            print(f"✗ Download failed: {stdout}")
            return False


class ArchiveOrgSearch:
    """Search and download ROMs from archive.org"""

    BASE_URL = "https://archive.org"
    SEARCH_API = f"{BASE_URL}/advancedsearch.php"

    # Common arcade ROM collections on archive.org
    ARCADE_COLLECTIONS = [
        "MAME_0.139_ROMS_(arcade_only)",
        "MAME_0.37b5_ROMs_(MAME_2000)",
        "MAME_2003_Reference_Set_MAME_0.78_ROMs",
        "MAME_0.151_Software_List_ROMs_(CHDs)",
        "FinalBurn_Neo_-_Arcade_Games",
    ]

    @classmethod
    def search_roms(cls, query: str, collection: Optional[str] = None, max_results: int = 50) -> List[Dict]:
        """
        Search for ROMs on archive.org

        Args:
            query: Search term
            collection: Specific collection to search (optional)
            max_results: Maximum number of results

        Returns:
            List of search results with metadata
        """
        # Build search query
        search_query = f"({query})"
        if collection:
            search_query += f" AND collection:({collection})"
        else:
            # Search across common arcade collections
            collections_str = " OR ".join(cls.ARCADE_COLLECTIONS)
            search_query += f" AND collection:({collections_str})"

        params = {
            'q': search_query,
            'fl[]': ['identifier', 'title', 'downloads', 'item_size', 'publicdate'],
            'rows': max_results,
            'output': 'json',
            'sort[]': 'downloads desc'
        }

        try:
            response = requests.get(cls.SEARCH_API, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('response', {}).get('docs', [])
        except Exception as e:
            print(f"Search failed: {e}")
            return []

    @classmethod
    def get_item_files(cls, identifier: str) -> List[Dict]:
        """
        Get list of files for a specific item

        Args:
            identifier: Archive.org item identifier

        Returns:
            List of files with metadata
        """
        metadata_url = f"{cls.BASE_URL}/metadata/{identifier}"
        try:
            response = requests.get(metadata_url)
            response.raise_for_status()
            data = response.json()
            return data.get('files', [])
        except Exception as e:
            print(f"Failed to get item files: {e}")
            return []

    @classmethod
    def get_download_url(cls, identifier: str, filename: str) -> str:
        """
        Construct download URL for a file

        Args:
            identifier: Archive.org item identifier
            filename: Name of file to download

        Returns:
            Direct download URL
        """
        return f"{cls.BASE_URL}/download/{identifier}/{filename}"

    @classmethod
    def download_file(cls, url: str, output_path: str, show_progress: bool = True):
        """
        Download file from archive.org

        Args:
            url: Download URL
            output_path: Local path to save file
            show_progress: Show progress bar
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if show_progress and total_size > 0:
                with open(output_path, 'wb') as f, tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    desc=os.path.basename(output_path)
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        pbar.update(len(chunk))
            else:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            print(f"✓ Downloaded: {output_path}")
            return True
        except Exception as e:
            print(f"✗ Download failed: {e}")
            return False


class DownloadQueue:
    """Manage queue of downloads"""

    def __init__(self, queue_file: str = 'download_queue.json'):
        self.queue_file = queue_file
        self.queue = []
        self.load_queue()

    def load_queue(self):
        """Load queue from file"""
        if os.path.exists(self.queue_file):
            with open(self.queue_file, 'r') as f:
                self.queue = json.load(f)

    def save_queue(self):
        """Save queue to file"""
        with open(self.queue_file, 'w') as f:
            json.dump(self.queue, f, indent=2)

    def add(self, url: str, system: str, filename: Optional[str] = None):
        """Add item to download queue"""
        item = {
            'url': url,
            'system': system,
            'filename': filename or os.path.basename(urlparse(url).path),
            'status': 'pending'
        }
        self.queue.append(item)
        self.save_queue()
        print(f"✓ Added to queue: {item['filename']}")

    def list_queue(self):
        """Display current queue"""
        if not self.queue:
            print("Queue is empty")
            return

        print("\nDownload Queue:")
        print("-" * 80)
        for idx, item in enumerate(self.queue, 1):
            status_icon = "✓" if item['status'] == 'completed' else "⋯"
            print(f"{idx}. [{status_icon}] {item['filename']}")
            print(f"   System: {item['system']} | Status: {item['status']}")
            print(f"   URL: {item['url']}")
        print("-" * 80)

    def clear_completed(self):
        """Remove completed items from queue"""
        self.queue = [item for item in self.queue if item['status'] != 'completed']
        self.save_queue()

    def process_queue(self, batocera: BatoceraManager, direct_download: bool = True):
        """
        Process all items in queue

        Args:
            batocera: BatoceraManager instance
            direct_download: Download directly to Batocera (faster)
        """
        pending_items = [item for item in self.queue if item['status'] == 'pending']

        if not pending_items:
            print("No pending downloads in queue")
            return

        print(f"\nProcessing {len(pending_items)} downloads...")

        for item in pending_items:
            print(f"\nProcessing: {item['filename']}")

            if direct_download:
                success = batocera.download_to_batocera(
                    item['url'],
                    item['system'],
                    item['filename']
                )
            else:
                # Download locally then transfer
                local_path = f"/tmp/{item['filename']}"
                if ArchiveOrgSearch.download_file(item['url'], local_path):
                    remote_path = f"{batocera.rom_base_path}/{item['system']}/{item['filename']}"
                    batocera.create_directory(item['system'])
                    batocera.transfer_file(local_path, remote_path)
                    os.remove(local_path)
                    success = True
                else:
                    success = False

            item['status'] = 'completed' if success else 'failed'
            self.save_queue()

        print("\n✓ Queue processing complete")


def format_size(bytes_size):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def main():
    parser = argparse.ArgumentParser(
        description='Batocera Arcade Game Downloader',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for a game
  %(prog)s search "street fighter" --host 192.168.1.100

  # Download from URL
  %(prog)s download --url "https://archive.org/download/..." --system mame --host 192.168.1.100

  # Add to queue
  %(prog)s queue add --url "https://archive.org/download/..." --system mame

  # Process queue
  %(prog)s queue process --host 192.168.1.100

  # List systems on Batocera
  %(prog)s list-systems --host 192.168.1.100
        """
    )

    parser.add_argument('--host', help='Batocera cabinet IP address')
    parser.add_argument('--username', default='root', help='SSH username (default: root)')
    parser.add_argument('--password', default='linux', help='SSH password (default: linux)')
    parser.add_argument('--port', type=int, default=22, help='SSH port (default: 22)')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for ROMs on archive.org')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--collection', help='Specific collection to search')
    search_parser.add_argument('--max-results', type=int, default=20, help='Max results (default: 20)')

    # Download command
    download_parser = subparsers.add_parser('download', help='Download ROM to Batocera')
    download_parser.add_argument('--url', required=True, help='Download URL')
    download_parser.add_argument('--system', required=True, help='Target system (e.g., mame, fba)')
    download_parser.add_argument('--filename', help='Custom filename')
    download_parser.add_argument('--local', action='store_true', help='Download locally then transfer')

    # Queue commands
    queue_parser = subparsers.add_parser('queue', help='Manage download queue')
    queue_subparsers = queue_parser.add_subparsers(dest='queue_command')

    queue_add = queue_subparsers.add_parser('add', help='Add to queue')
    queue_add.add_argument('--url', required=True, help='Download URL')
    queue_add.add_argument('--system', required=True, help='Target system')
    queue_add.add_argument('--filename', help='Custom filename')

    queue_subparsers.add_parser('list', help='List queue')
    queue_subparsers.add_parser('clear', help='Clear completed items')

    queue_process = queue_subparsers.add_parser('process', help='Process queue')
    queue_process.add_argument('--local', action='store_true', help='Download locally then transfer')

    # List systems command
    subparsers.add_parser('list-systems', help='List available systems on Batocera')

    # Browse item command
    browse_parser = subparsers.add_parser('browse', help='Browse files in archive.org item')
    browse_parser.add_argument('identifier', help='Archive.org item identifier')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Handle queue commands that don't need connection
    if args.command == 'queue':
        queue = DownloadQueue()

        if args.queue_command == 'add':
            queue.add(args.url, args.system, args.filename)
            return
        elif args.queue_command == 'list':
            queue.list_queue()
            return
        elif args.queue_command == 'clear':
            queue.clear_completed()
            print("✓ Cleared completed items")
            return
        elif args.queue_command == 'process':
            if not args.host:
                print("Error: --host is required for queue processing")
                return
            batocera = BatoceraManager(args.host, args.username, args.password, args.port)
            if batocera.connect():
                queue.process_queue(batocera, direct_download=not args.local)
                batocera.disconnect()
            return

    # Handle search command
    if args.command == 'search':
        print(f"Searching archive.org for: {args.query}")
        results = ArchiveOrgSearch.search_roms(args.query, args.collection, args.max_results)

        if not results:
            print("No results found")
            return

        print(f"\nFound {len(results)} results:\n")
        for idx, item in enumerate(results, 1):
            title = item.get('title', 'Unknown')
            identifier = item.get('identifier', '')
            downloads = item.get('downloads', 0)
            size = format_size(int(item.get('item_size', 0)))

            print(f"{idx}. {title}")
            print(f"   ID: {identifier}")
            print(f"   Downloads: {downloads:,} | Size: {size}")
            print(f"   URL: https://archive.org/details/{identifier}\n")

        return

    # Handle browse command
    if args.command == 'browse':
        print(f"Browsing files for: {args.identifier}")
        files = ArchiveOrgSearch.get_item_files(args.identifier)

        if not files:
            print("No files found")
            return

        # Filter for common ROM formats
        rom_formats = ['.zip', '.7z', '.bin', '.iso', '.chd']
        rom_files = [f for f in files if any(f['name'].endswith(ext) for ext in rom_formats)]

        print(f"\nFound {len(rom_files)} ROM files:\n")
        for idx, file in enumerate(rom_files, 1):
            name = file.get('name', 'Unknown')
            size = format_size(int(file.get('size', 0)))
            url = ArchiveOrgSearch.get_download_url(args.identifier, name)

            print(f"{idx}. {name} ({size})")
            print(f"   {url}\n")

        return

    # Commands that require Batocera connection
    if not args.host:
        print("Error: --host is required for this command")
        return

    batocera = BatoceraManager(args.host, args.username, args.password, args.port)

    if not batocera.connect():
        return

    try:
        if args.command == 'download':
            batocera.download_to_batocera(
                args.url,
                args.system,
                args.filename
            )

        elif args.command == 'list-systems':
            systems = batocera.list_systems()
            print("\nAvailable systems on Batocera:")
            for system in systems:
                print(f"  - {system}")

    finally:
        batocera.disconnect()


if __name__ == '__main__':
    main()
