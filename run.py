#!/usr/bin/env python3
"""
FS25 Mod Monitor - Task Runner
Cross-platform task runner for common operations
Usage: python run.py <command>
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50 + "\n")

def run_command(cmd, description=None):
    """Run a shell command"""
    if description:
        print(f"🔄 {description}...")
    
    result = subprocess.run(cmd, shell=True, capture_output=False)
    return result.returncode == 0

def show_help():
    """Display help information"""
    print_header("FS25 Mod Monitor - Available Commands")
    
    print("Setup & Installation:")
    print("  python run.py install       - Install Python dependencies")
    print("  python run.py setup         - First-time setup")
    print("")
    print("Testing:")
    print("  python run.py test          - Run all tests")
    print("  python run.py test-ftp      - Test FTP/SFTP connection")
    print("  python run.py test-discord  - Test Discord webhook")
    print("  python run.py test-mod      - Test mod parser (requires mod.zip path)")
    print("")
    print("Running:")
    print("  python run.py run           - Run the mod monitor once")
    print("  python run.py monitor       - Same as run")
    print("")
    print("Maintenance:")
    print("  python run.py update        - Pull latest from GitHub")
    print("  python run.py clean         - Remove cache files")
    print("  python run.py status        - Show configuration status")
    print("")

def install():
    """Install dependencies"""
    print_header("Installing Dependencies")
    
    if not Path("requirements.txt").exists():
        print("✗ requirements.txt not found!")
        return False
    
    success = run_command("pip install -r requirements.txt", "Installing packages")
    
    if success:
        print("\n✅ Dependencies installed successfully!")
    else:
        print("\n❌ Installation failed")
    
    return success

def setup():
    """First-time setup"""
    print_header("Setting Up FS25 Mod Monitor")
    
    # Check if config.py exists
    if not Path("config.py").exists():
        if Path("config.example.py").exists():
            shutil.copy("config.example.py", "config.py")
            print("✅ Created config.py from template")
            print("⚠️  Please edit config.py with your credentials!")
        else:
            print("✗ config.example.py not found!")
            return False
    else:
        print("✅ config.py already exists")
    
    # Install dependencies
    print("")
    install()
    
    print("\n" + "=" * 50)
    print("✅ Setup Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("  1. Edit config.py with your server credentials")
    print("  2. Run 'python run.py test' to verify connections")
    print("  3. Run 'python run.py run' to start monitoring")
    
    return True

def test_all():
    """Run all tests"""
    print_header("Running All Tests")
    
    test_ftp()
    print("")
    test_discord()
    
    print("\n✅ All tests complete!")

def test_ftp():
    """Test FTP connection"""
    print_header("Testing FTP/SFTP Connection")
    
    if not Path("test_connection.py").exists():
        print("✗ test_connection.py not found!")
        return False
    
    return run_command("python test_connection.py")

def test_discord():
    """Test Discord webhook"""
    print_header("Testing Discord Webhook")
    
    if not Path("test_discord.py").exists():
        print("✗ test_discord.py not found!")
        return False
    
    return run_command("python test_discord.py")

def test_mod():
    """Test mod parser"""
    print_header("Testing Mod Parser")
    
    if not Path("test_mod_parser.py").exists():
        print("✗ test_mod_parser.py not found!")
        return False
    
    if len(sys.argv) < 3:
        print("Usage: python run.py test-mod <path_to_mod.zip>")
        print("\nExample:")
        print("  python run.py test-mod ./mods/FS25_SomeMod.zip")
        return False
    
    mod_path = sys.argv[2]
    return run_command(f"python test_mod_parser.py {mod_path}")

def run_monitor():
    """Run the mod monitor"""
    print_header("Running FS25 Mod Monitor")
    
    if not Path("fs25_mod_monitor.py").exists():
        print("✗ fs25_mod_monitor.py not found!")
        return False
    
    return run_command("python fs25_mod_monitor.py")

def update():
    """Update from GitHub"""
    print_header("Updating from GitHub")
    
    success = run_command("git pull origin main", "Pulling latest changes")
    
    if success:
        print("\n✅ Updated to latest version!")
        print("Run 'python run.py run' to use the updated version")
    else:
        print("\n❌ Update failed")
    
    return success

def clean():
    """Clean cache and temporary files"""
    print_header("Cleaning Up")
    
    patterns = [
        ("__pycache__", "directory"),
        ("*.pyc", "file"),
        ("*.pyo", "file"),
        ("*.log", "file"),
    ]
    
    cleaned = 0
    
    for pattern, item_type in patterns:
        if item_type == "directory":
            for path in Path(".").rglob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                    cleaned += 1
                    print(f"  Removed: {path}")
        else:  # file
            for path in Path(".").rglob(pattern):
                if path.is_file():
                    path.unlink()
                    cleaned += 1
                    print(f"  Removed: {path}")
    
    print(f"\n✅ Cleaned {cleaned} items!")

def status():
    """Show configuration status"""
    print_header("FS25 Mod Monitor - Configuration Status")
    
    # Check config.py
    if Path("config.py").exists():
        print("✅ config.py exists")
        try:
            import config
            print(f"   Host: {config.SFTP_HOST}")
            print(f"   Port: {config.SFTP_PORT}")
            print(f"   Path: {config.SFTP_MODS_PATH}")
        except Exception as e:
            print(f"   ⚠️  Error reading config: {e}")
    else:
        print("❌ config.py not found - run 'python run.py setup'")
    
    print("")
    
    # Check mod_state.json
    if Path("mod_state.json").exists():
        print("✅ mod_state.json exists (monitoring active)")
        try:
            import json
            with open("mod_state.json") as f:
                data = json.load(f)
                print(f"   Tracking {len(data)} mods")
        except Exception as e:
            print(f"   ⚠️  Error reading state: {e}")
    else:
        print("ℹ️  mod_state.json not found (first run pending)")
    
    print("")

def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    commands = {
        "help": show_help,
        "install": install,
        "setup": setup,
        "test": test_all,
        "test-ftp": test_ftp,
        "test-discord": test_discord,
        "run": run_monitor,
        "monitor": run_monitor,
        "update": update,
        "clean": clean,
        "status": status,
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"❌ Unknown command: {command}")
        print("")
        show_help()

if __name__ == "__main__":
    main()
