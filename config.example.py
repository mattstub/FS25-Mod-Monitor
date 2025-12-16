"""
Configuration Template for FS25 Mod Monitor
Copy this file to config.py and fill in your actual values
"""

# SFTP Connection Settings
SFTP_HOST = "your-gportal-server.com"       # Your G-Portal server address
SFTP_PORT = 22                              # Usually 22 for SFTP
SFTP_USERNAME = "your_username"             # Your G-Portal SFTP username
SFTP_PASSWORD = "your_password"             # Your G-Portal SFTP password
SFTP_MODS_PATH = "/path/to/mods"            # Path to mods folder (e.g., "/mods")

# Connection Type (Optional - script will auto-detect if not set)
# USE_FTP = True   # Force FTP mode
# USE_FTP = False  # Force SFTP mode
# USE_FTP = None   # Auto-detect (default)

# Discord Webhook
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"

# Monitoring Settings (optional customization)
STATE_FILE = "mod_state.json"              # File to store mod state between runs
