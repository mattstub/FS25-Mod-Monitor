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
from ftplib import FTP, FTP_TLS

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

# FTP/SFTP mode selection (will auto-detect)
USE_FTP = getattr(config, 'USE_FTP', None)  # Can be True, False, or None (auto-detect)

# =========================
# FUNCTIONS
# =========================

def connect_ftp():
    """Establish FTP connection to the server"""
    try:
        # Try FTP with TLS first (more secure)
        try:
            ftp = FTP_TLS()
            ftp.connect(SFTP_HOST, SFTP_PORT if SFTP_PORT != 22 else 21)
            ftp.login(SFTP_USERNAME, SFTP_PASSWORD)
            ftp.prot_p()  # Enable encryption
            print(f"✓ Connected to {SFTP_HOST} (using FTPS)")
            return ftp, 'ftp'
        except:
            # Fall back to plain FTP
            ftp = FTP()
            ftp.connect(SFTP_HOST, SFTP_PORT if SFTP_PORT != 22 else 21)
            ftp.login(SFTP_USERNAME, SFTP_PASSWORD)
            print(f"✓ Connected to {SFTP_HOST} (using FTP)")
            return ftp, 'ftp'
    except Exception as e:
        print(f"✗ FTP Connection failed: {e}")
        return None, None

def connect_sftp():
    """Establish SFTP connection to the server"""
    try:
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        
        # Try SSH key authentication first (more secure)
        try:
            key_path = os.path.expanduser('~/.ssh/id_rsa')
            if os.path.exists(key_path):
                private_key = paramiko.RSAKey.from_private_key_file(key_path)
                transport.connect(username=SFTP_USERNAME, pkey=private_key)
                print(f"✓ Connected to {SFTP_HOST} (using SSH key)")
            else:
                transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
                print(f"✓ Connected to {SFTP_HOST} (using password)")
        except paramiko.ssh_exception.AuthenticationException:
            transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
            print(f"✓ Connected to {SFTP_HOST} (using password)")
        
        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp, transport
    except Exception as e:
        print(f"✗ SFTP Connection failed: {e}")
        return None, None

def connect_server():
    """Auto-detect and connect to server using FTP or SFTP"""
    global USE_FTP
    
    # If user specified FTP/SFTP in config, use that
    if USE_FTP is True:
        return connect_ftp()
    elif USE_FTP is False:
        client, transport = connect_sftp()
        return client, 'sftp' if client else None
    
    # Auto-detect: try SFTP first (port 22), then FTP
    print("Auto-detecting connection type...")
    
    if SFTP_PORT == 22:
        print("Trying SFTP (port 22)...")
        client, transport = connect_sftp()
        if client:
            return client, 'sftp'
        
        print("SFTP failed, trying FTP (port 21)...")
        return connect_ftp()
    else:
        # Non-standard port, try FTP first
        print(f"Trying FTP (port {SFTP_PORT})...")
        client, conn_type = connect_ftp()
        if client:
            return client, conn_type
        
        print("FTP failed, trying SFTP...")
        client, transport = connect_sftp()
        return (client, 'sftp') if client else (None, None)

def extract_mod_info(client, conn_type, remote_file_path, file_size):
    """
    Extract mod information from modDesc.xml inside the zip file
    Works with both FTP and SFTP
    Returns: dict with title, version, author, filesize
    """
    try:
        # Download the zip file to memory
        zip_data = io.BytesIO()
        
        if conn_type == 'sftp':
            with client.file(remote_file_path, 'r') as remote_file:
                zip_data.write(remote_file.read())
        else:  # FTP
            client.retrbinary(f'RETR {remote_file_path}', zip_data.write)
        
        zip_data.seek(0)
                
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

def get_current_mods(client, conn_type):
    """
    Scan the mods directory and return a dict of current mods with their info
    Works with both FTP and SFTP
    Key: filename, Value: {title, version, author, filesize}
    """
    current_mods = {}

    try:
        if conn_type == 'sftp':
            # SFTP method
            files = client.listdir_attr(SFTP_MODS_PATH)
            
            for file_attr in files:
                filename = file_attr.filename
                
                # Only process .zip files
                if not filename.lower().endswith('.zip'):
                    continue
                
                file_size = file_attr.st_size
                remote_path = f"{SFTP_MODS_PATH}/{filename}"
                
                print(f"  Scanning: {filename}")
                mod_info = extract_mod_info(client, conn_type, remote_path, file_size)
                current_mods[filename] = mod_info

        else:  # FTP
            # Change to mods directory
            client.cwd(SFTP_MODS_PATH)

            # Get file listing with detailed info
            file_list = []

            def parse_line(line):
                """Callback to collect directory listing lines"""
                file_list.append(line)
            
            client.dir(parse_line)       
            
            # Parse each file in the listing
            for file_line in file_list:
                # Parse FTP LIST output 
                 # Typical format: -rw-r--r-- 1 owner group size month day time filename
                # or: drwxr-xr-x 2 owner group size month day time foldername
                parts = file_line.split()

                if len(parts) < 9:
                    continue

                # Skip directories (first char is 'd')
                if parts[0].startswith('d'):
                    continue               

                filename = parts[-1]
                
                # Only process .zip files
                if not filename.lower().endswith('.zip'):
                    continue
                
                # Get file size (varies by FTP server format, usually 5th column)
                try:
                    # Try to find the size - it's usually the first number-only field
                    file_size = None
                    for part in parts[1:8]:  # Size is typically in first 8 columns
                        if part.isdigit():
                            file_size = int(part)
                            break

                     if file_size is None:
                        # Fallback: assume 5th position (index 4)
                        file_size = int(parts[4])                   
                except (ValueError, IndexError):
                    print(f"  Warning: Could not determine size for {filename}, using 0")
                    file_size = 0

                remote_path = f"{SFTP_MODS_PATH}/{filename}"
                
                print(f"  Scanning: {filename}")
                mod_info = extract_mod_info(client, conn_type, remote_path, file_size)
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
    
    # Connect to server (auto-detects FTP or SFTP)
    client, conn_type = connect_server()
    if not client:
        return
    
    try:
        # Get current mods
        current_mods = get_current_mods(client, conn_type)
        
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
        if conn_type == 'sftp':
            client.close()
            # Note: transport is not returned in new structure, 
            # but SFTP client close should handle cleanup
        else:  # FTP
            client.quit()
        print("\n✓ Connection closed")
    
    print("\n" + "="*50)
    print("Check Complete")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
