"""
Farming Simulator 25 Mod Monitor
Tracks mod changes (add/remove/update) via SFTP and posts to Discord
"""

import paramiko
import json
import os
import zipfile
import io
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import requests

# Import configuration
try:
    import config
except ImportError:
    print("ERROR: config.py not found!")
    print("Please copy config.example.py to config.py and fill in your credentials.")
    exit(1)

# Load configuration from config.py
SFTP_HOST = config.SFTP_HOST
SFTP_PORT = config.SFTP_PORT
SFTP_USERNAME = config.SFTP_USERNAME
SFTP_PASSWORD = config.SFTP_PASSWORD
SFTP_MODS_PATH = config.SFTP_MODS_PATH
DISCORD_WEBHOOK_URL = config.DISCORD_WEBHOOK_URL
STATE_FILE = config.STATE_FILE

# =========================
# FUNCTIONS
# =========================

def connect_sftp():
    """Establish SFTP connection to the server"""
    try:
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print(f"✓ Connected to {SFTP_HOST}")
        return sftp, transport
    except Exception as e:
        print(f"✗ SFTP Connection failed: {e}")
        return None, None

def extract_mod_info(sftp, remote_file_path, file_size):
    """
    Extract mod information from modDesc.xml inside the zip file
    Returns: dict with title, version, author, filesize
    """
    try:
        # Download the zip file to memory
        with sftp.file(remote_file_path, 'r') as remote_file:
            zip_data = io.BytesIO(remote_file.read())
        
        # Open zip and extract modDesc.xml
        with zipfile.ZipFile(zip_data, 'r') as zip_ref:
            # Try to find modDesc.xml (case-insensitive)
            mod_desc_name = None
            for name in zip_ref.namelist():
                if name.lower().endswith('moddesc.xml'):
                    mod_desc_name = name
                    break
            
            if not mod_desc_name:
                return {
                    'title': Path(remote_file_path).stem,
                    'version': 'Unknown',
                    'author': 'Unknown',
                    'filesize': file_size
                }
            
            # Parse the XML
            with zip_ref.open(mod_desc_name) as xml_file:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # Extract mod information
                title = root.find('.//title/en')
                if title is None:
                    title = root.find('.//title')
                title = title.text if title is not None else Path(remote_file_path).stem
                
                version = root.get('descVersion', 'Unknown')
                
                author = root.find('.//author')
                author = author.text if author is not None else 'Unknown'
                
                return {
                    'title': title,
                    'version': version,
                    'author': author,
                    'filesize': file_size
                }
    
    except Exception as e:
        print(f"  Warning: Could not parse {remote_file_path}: {e}")
        return {
            'title': Path(remote_file_path).stem,
            'version': 'Unknown',
            'author': 'Unknown',
            'filesize': file_size
        }

def get_current_mods(sftp):
    """
    Scan the mods directory and return a dict of current mods with their info
    Key: filename, Value: {title, version, author, filesize}
    """
    current_mods = {}
    
    try:
        files = sftp.listdir_attr(SFTP_MODS_PATH)
        
        for file_attr in files:
            filename = file_attr.filename
            
            # Only process .zip files
            if not filename.lower().endswith('.zip'):
                continue
            
            file_size = file_attr.st_size
            remote_path = f"{SFTP_MODS_PATH}/{filename}"
            
            print(f"  Scanning: {filename}")
            mod_info = extract_mod_info(sftp, remote_path, file_size)
            current_mods[filename] = mod_info
        
        print(f"✓ Found {len(current_mods)} mods")
        return current_mods
    
    except Exception as e:
        print(f"✗ Error scanning mods directory: {e}")
        return {}

def load_previous_state():
    """Load the previous state from JSON file"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_current_state(mods):
    """Save current state to JSON file"""
    with open(STATE_FILE, 'w') as f:
        json.dump(mods, f, indent=2)

def format_file_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def detect_changes(previous_mods, current_mods):
    """
    Compare previous and current states to detect changes
    Returns: list of change dictionaries
    """
    changes = []
    
    # Detect additions
    for filename, info in current_mods.items():
        if filename not in previous_mods:
            changes.append({
                'type': 'added',
                'filename': filename,
                'info': info
            })
        # Detect updates (version or filesize changed)
        elif (info['version'] != previous_mods[filename]['version'] or 
              info['filesize'] != previous_mods[filename]['filesize']):
            changes.append({
                'type': 'updated',
                'filename': filename,
                'info': info,
                'old_version': previous_mods[filename]['version']
            })
    
    # Detect removals
    for filename in previous_mods:
        if filename not in current_mods:
            changes.append({
                'type': 'removed',
                'filename': filename,
                'info': previous_mods[filename]
            })
    
    return changes

def send_discord_notification(changes, current_mods):
    """Send changes to Discord via webhook"""
    if not changes:
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    # Calculate summary statistics
    total_mods = len(current_mods)
    total_size = sum(mod['filesize'] for mod in current_mods.values())
    
    # Prepare embed
    embed = {
        "title": "🚜 Farming Simulator 25 - Mod Changes Detected",
        "color": 0x00FF00 if any(c['type'] == 'added' for c in changes) else 0xFF9900,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": f"Checked at {timestamp}"
        },
        "fields": []
    }
    
    # Group changes by type
    for change in changes:
        change_type = change['type']
        info = change['info']
        
        if change_type == 'added':
            emoji = "✅"
            color_indicator = "**[ADDED]**"
        elif change_type == 'removed':
            emoji = "🗑️"
            color_indicator = "**[REMOVED]**"
        else:  # updated
            emoji = "🔄"
            color_indicator = "**[UPDATED]**"
        
        field_value = f"**Title:** {info['title']}\n"
        field_value += f"**Version:** {info['version']}"
        
        if change_type == 'updated' and 'old_version' in change:
            field_value += f" (was {change['old_version']})"
        
        field_value += f"\n**Author:** {info['author']}\n"
        field_value += f"**Size:** {format_file_size(info['filesize'])}"
        
        embed["fields"].append({
            "name": f"{emoji} {color_indicator} {change['filename']}",
            "value": field_value,
            "inline": False
        })
    
    # Add summary section at the end
    summary_value = f"**Total Mods on Server:** {total_mods}\n"
    summary_value += f"**Total Size:** {format_file_size(total_size)}"
    
    embed["fields"].append({
        "name": "📊 Current Server Status",
        "value": summary_value,
        "inline": False
    })
    
    # Send to Discord
    payload = {
        "embeds": [embed]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"✓ Discord notification sent ({len(changes)} changes)")
        else:
            print(f"✗ Discord notification failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Discord notification error: {e}")

def main():
    """Main monitoring function"""
    print("\n" + "="*50)
    print("FS25 Mod Monitor - Starting Check")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
    print("="*50 + "\n")
    
    # Connect to SFTP
    sftp, transport = connect_sftp()
    if not sftp:
        return
    
    try:
        # Get current mods
        current_mods = get_current_mods(sftp)
        
        # Load previous state
        previous_mods = load_previous_state()
        
        # Detect changes
        changes = detect_changes(previous_mods, current_mods)
        
        if changes:
            print(f"\n✓ Detected {len(changes)} change(s)")
            for change in changes:
                print(f"  - {change['type'].upper()}: {change['filename']}")
            
            # Send Discord notification
            send_discord_notification(changes, current_mods)
        else:
            print("\n✓ No changes detected")
        
        # Save current state
        save_current_state(current_mods)
        
    finally:
        # Close connection
        sftp.close()
        transport.close()
        print("\n✓ Connection closed")
    
    print("\n" + "="*50)
    print("Check Complete")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
