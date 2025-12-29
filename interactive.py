#!/usr/bin/env python3
"""
Interactive menu for Batocera Arcade Downloader
Provides a user-friendly interface for common operations
"""

import sys
import os
from arcade_downloader import (
    BatoceraManager,
    ArchiveOrgSearch,
    DownloadQueue,
    format_size
)


class InteractiveMenu:
    def __init__(self):
        self.batocera_host = None
        self.batocera_user = 'root'
        self.batocera_pass = 'linux'
        self.batocera = None
        self.queue = DownloadQueue()

    def clear_screen(self):
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_header(self, title):
        self.clear_screen()
        print("=" * 60)
        print(f"  {title}")
        print("=" * 60)
        print()

    def get_input(self, prompt, default=None):
        if default:
            prompt = f"{prompt} [{default}]: "
        else:
            prompt = f"{prompt}: "

        value = input(prompt).strip()
        return value if value else default

    def setup_connection(self):
        self.print_header("Batocera Connection Setup")

        if self.batocera_host:
            print(f"Current host: {self.batocera_host}")
            change = self.get_input("Change connection? (y/n)", "n")
            if change.lower() != 'y':
                return

        self.batocera_host = self.get_input("Enter Batocera IP address", self.batocera_host)
        self.batocera_user = self.get_input("Username", self.batocera_user)
        self.batocera_pass = self.get_input("Password", self.batocera_pass)

        print("\nTesting connection...")
        self.batocera = BatoceraManager(
            self.batocera_host,
            self.batocera_user,
            self.batocera_pass
        )

        if self.batocera.connect():
            self.batocera.disconnect()
            print("\n✓ Connection successful!")
        else:
            print("\n✗ Connection failed!")
            self.batocera_host = None
            self.batocera = None

        input("\nPress Enter to continue...")

    def search_roms(self):
        self.print_header("Search Archive.org for ROMs")

        query = self.get_input("Enter search term")
        if not query:
            return

        max_results = int(self.get_input("Max results", "20"))

        print(f"\nSearching for: {query}...")
        results = ArchiveOrgSearch.search_roms(query, max_results=max_results)

        if not results:
            print("No results found")
            input("\nPress Enter to continue...")
            return

        while True:
            self.print_header(f"Search Results: {query}")
            print(f"Found {len(results)} results:\n")

            for idx, item in enumerate(results, 1):
                title = item.get('title', 'Unknown')
                identifier = item.get('identifier', '')
                downloads = item.get('downloads', 0)
                size = format_size(int(item.get('item_size', 0)))

                print(f"{idx}. {title}")
                print(f"   Downloads: {downloads:,} | Size: {size}")
                print(f"   ID: {identifier}\n")

            print("\nOptions:")
            print("  [number] - Browse files in item")
            print("  [q] - Back to main menu")

            choice = self.get_input("\nSelect option")

            if choice.lower() == 'q':
                break

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(results):
                    self.browse_item(results[idx]['identifier'])
            except ValueError:
                continue

    def browse_item(self, identifier):
        self.print_header(f"Browse: {identifier}")

        print("Loading files...")
        files = ArchiveOrgSearch.get_item_files(identifier)

        # Filter for ROM formats
        rom_formats = ['.zip', '.7z', '.bin', '.iso', '.chd']
        rom_files = [f for f in files if any(f['name'].endswith(ext) for ext in rom_formats)]

        if not rom_files:
            print("No ROM files found")
            input("\nPress Enter to continue...")
            return

        while True:
            self.print_header(f"Files: {identifier}")
            print(f"Found {len(rom_files)} ROM files:\n")

            for idx, file in enumerate(rom_files, 1):
                name = file.get('name', 'Unknown')
                size = format_size(int(file.get('size', 0)))
                print(f"{idx}. {name} ({size})")

            print("\nOptions:")
            print("  [number] - Download/queue file")
            print("  [q] - Back")

            choice = self.get_input("\nSelect option")

            if choice.lower() == 'q':
                break

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(rom_files):
                    file = rom_files[idx]
                    url = ArchiveOrgSearch.get_download_url(identifier, file['name'])
                    self.download_menu(url, file['name'])
            except ValueError:
                continue

    def download_menu(self, url, filename):
        self.print_header(f"Download: {filename}")

        print(f"URL: {url}\n")
        print("Options:")
        print("  1. Download now")
        print("  2. Add to queue")
        print("  3. Cancel")

        choice = self.get_input("\nSelect option")

        if choice == '1':
            self.download_now(url, filename)
        elif choice == '2':
            self.add_to_queue(url, filename)

    def download_now(self, url, filename):
        if not self.batocera_host:
            print("\nPlease setup Batocera connection first")
            input("\nPress Enter to continue...")
            return

        system = self.get_input("Target system (e.g., mame, fba, neogeo)", "mame")

        print("\nConnecting to Batocera...")
        batocera = BatoceraManager(
            self.batocera_host,
            self.batocera_user,
            self.batocera_pass
        )

        if batocera.connect():
            batocera.download_to_batocera(url, system, filename)
            batocera.disconnect()
        else:
            print("Failed to connect to Batocera")

        input("\nPress Enter to continue...")

    def add_to_queue(self, url, filename):
        system = self.get_input("Target system (e.g., mame, fba, neogeo)", "mame")
        self.queue.add(url, system, filename)
        input("\nPress Enter to continue...")

    def manage_queue(self):
        while True:
            self.print_header("Download Queue")

            if not self.queue.queue:
                print("Queue is empty\n")
            else:
                for idx, item in enumerate(self.queue.queue, 1):
                    status_icon = "✓" if item['status'] == 'completed' else "⋯"
                    print(f"{idx}. [{status_icon}] {item['filename']}")
                    print(f"    System: {item['system']} | Status: {item['status']}\n")

            print("Options:")
            print("  1. Add to queue manually")
            print("  2. Process queue")
            print("  3. Clear completed")
            print("  4. Back to main menu")

            choice = self.get_input("\nSelect option")

            if choice == '1':
                self.add_to_queue_manual()
            elif choice == '2':
                self.process_queue()
            elif choice == '3':
                self.queue.clear_completed()
                print("✓ Cleared completed items")
                input("\nPress Enter to continue...")
            elif choice == '4':
                break

    def add_to_queue_manual(self):
        self.print_header("Add to Queue")

        url = self.get_input("Download URL")
        if not url:
            return

        system = self.get_input("Target system", "mame")
        filename = self.get_input("Filename (optional)")

        self.queue.add(url, system, filename)
        input("\nPress Enter to continue...")

    def process_queue(self):
        if not self.batocera_host:
            print("\nPlease setup Batocera connection first")
            input("\nPress Enter to continue...")
            return

        pending = [item for item in self.queue.queue if item['status'] == 'pending']
        if not pending:
            print("\nNo pending downloads in queue")
            input("\nPress Enter to continue...")
            return

        print(f"\nProcessing {len(pending)} downloads...")

        batocera = BatoceraManager(
            self.batocera_host,
            self.batocera_user,
            self.batocera_pass
        )

        if batocera.connect():
            self.queue.process_queue(batocera, direct_download=True)
            batocera.disconnect()
        else:
            print("Failed to connect to Batocera")

        input("\nPress Enter to continue...")

    def list_systems(self):
        if not self.batocera_host:
            print("\nPlease setup Batocera connection first")
            input("\nPress Enter to continue...")
            return

        self.print_header("Batocera Systems")

        print("Connecting to Batocera...")
        batocera = BatoceraManager(
            self.batocera_host,
            self.batocera_user,
            self.batocera_pass
        )

        if batocera.connect():
            systems = batocera.list_systems()
            print("\nAvailable systems:\n")
            for system in systems:
                print(f"  - {system}")
            batocera.disconnect()
        else:
            print("Failed to connect to Batocera")

        input("\nPress Enter to continue...")

    def main_menu(self):
        while True:
            self.print_header("Batocera Arcade Game Downloader")

            if self.batocera_host:
                print(f"Connected to: {self.batocera_host}\n")
            else:
                print("Not connected to Batocera\n")

            print("Main Menu:")
            print("  1. Setup Batocera connection")
            print("  2. Search for ROMs")
            print("  3. Manage download queue")
            print("  4. List Batocera systems")
            print("  5. Exit")

            choice = self.get_input("\nSelect option")

            if choice == '1':
                self.setup_connection()
            elif choice == '2':
                self.search_roms()
            elif choice == '3':
                self.manage_queue()
            elif choice == '4':
                self.list_systems()
            elif choice == '5':
                print("\nGoodbye!")
                sys.exit(0)

    def run(self):
        try:
            self.main_menu()
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            sys.exit(0)


if __name__ == '__main__':
    menu = InteractiveMenu()
    menu.run()
