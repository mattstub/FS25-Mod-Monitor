"""
Quick FTP/SFTP Connection Test
Tests your G-Portal credentials without running the full monitor
"""

from ftplib import FTP, FTP_TLS
import paramiko

# Import your config
try:
    import config
except ImportError:
    print("ERROR: config.py not found!")
    print("Make sure you're in the project directory with config.py")
    exit(1)

print("=" * 50)
print("FTP/SFTP Connection Test")
print("=" * 50)
print(f"\nHost: {config.SFTP_HOST}")
print(f"Port: {config.SFTP_PORT}")
print(f"Username: {config.SFTP_USERNAME}")
print(f"Mods Path: {config.SFTP_MODS_PATH}")
print("\n" + "=" * 50)

# Test FTP Connection
print("\n🔄 Testing FTP connection...")
try:
    # Try FTPS first
    try:
        ftp = FTP_TLS()
        ftp.connect(config.SFTP_HOST, config.SFTP_PORT)
        ftp.login(config.SFTP_USERNAME, config.SFTP_PASSWORD)
        ftp.prot_p()
        print("✅ FTPS connection successful!")
        conn_type = "FTPS"
    except:
        # Fall back to plain FTP
        ftp = FTP()
        ftp.connect(config.SFTP_HOST, config.SFTP_PORT)
        ftp.login(config.SFTP_USERNAME, config.SFTP_PASSWORD)
        print("✅ FTP connection successful!")
        conn_type = "FTP"
    
    # Test directory access
    print(f"\n🔄 Testing access to mods directory: {config.SFTP_MODS_PATH}")
    ftp.cwd(config.SFTP_MODS_PATH)
    print("✅ Can access mods directory!")
    
    # List files
    print(f"\n📁 Files in {config.SFTP_MODS_PATH}:")
    files = []
    ftp.dir(files.append)
    
    zip_count = 0
    for file_line in files:
        if '.zip' in file_line.lower():
            zip_count += 1
            # Print first 5 zip files
            if zip_count <= 5:
                parts = file_line.split()
                if len(parts) >= 9:
                    filename = parts[-1]
                    print(f"  - {filename}")
    
    if zip_count > 5:
        print(f"  ... and {zip_count - 5} more .zip files")
    
    print(f"\n✅ Found {zip_count} mod files (.zip)")
    
    ftp.quit()
    print(f"\n{'=' * 50}")
    print(f"✅ ALL TESTS PASSED using {conn_type}!")
    print(f"{'=' * 50}")
    
except Exception as e:
    print(f"\n❌ FTP connection failed: {e}")
    print("\nTroubleshooting:")
    print("  1. Check SFTP_HOST is correct (IP or hostname)")
    print("  2. Check SFTP_PORT (should be 21 for FTP)")
    print("  3. Verify SFTP_USERNAME and SFTP_PASSWORD")
    print("  4. Verify SFTP_MODS_PATH is correct")
    print("  5. Check if G-Portal server is online")

# Test SFTP Connection (if port 22)
if config.SFTP_PORT == 22:
    print("\n" + "=" * 50)
    print("\n🔄 Testing SFTP connection (port 22)...")
    try:
        transport = paramiko.Transport((config.SFTP_HOST, config.SFTP_PORT))
        transport.connect(username=config.SFTP_USERNAME, password=config.SFTP_PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        print("✅ SFTP connection successful!")
        
        # Test directory access
        print(f"\n🔄 Testing access to mods directory: {config.SFTP_MODS_PATH}")
        files = sftp.listdir(config.SFTP_MODS_PATH)
        print("✅ Can access mods directory!")
        
        zip_files = [f for f in files if f.lower().endswith('.zip')]
        print(f"\n✅ Found {len(zip_files)} mod files (.zip)")
        
        sftp.close()
        transport.close()
        
        print(f"\n{'=' * 50}")
        print("✅ SFTP CONNECTION WORKS TOO!")
        print(f"{'=' * 50}")
        
    except Exception as e:
        print(f"ℹ️ SFTP not available: {e}")
        print("   (This is OK if using FTP)")

print("\n✨ Connection test complete!")
