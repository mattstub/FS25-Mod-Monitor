# FS25 Mod Monitor 🚜

Automated monitoring system for Farming Simulator 25 server mods. Tracks mod additions, removals, and updates via SFTP and posts detailed notifications to Discord.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)

## Features

- **Automatic Mod Tracking** - Monitors your FS25 server's mod folder via SFTP
- **Detailed Change Detection** - Tracks added, removed, and updated mods
- **Rich Metadata** - Extracts mod title, version, author, and file size from modDesc.xml
- **Discord Integration** - Posts formatted notifications with change summaries
- **Server Status** - Shows total mod count and combined size with each notification
- **Scheduled Monitoring** - Runs hourly (or custom interval) to catch all changes
- **Secure** - Credentials stored separately from code

## Example Discord Notification

```
🚜 Farming Simulator 25 - Mod Changes Detected

✅ [ADDED] FS25_JohnDeere8R.zip
Title: John Deere 8R Series
Version: 1.0.0.2
Author: GIANTS Software
Size: 45.23 MB

📊 Current Server Status
Total Mods on Server: 24
Total Size: 1.23 GB

Checked at 2024-12-16 02:00 PM
```

## Prerequisites

- Python 3.7 or higher
- SFTP access to your G-Portal server
- Discord webhook for notifications
- PythonAnywhere account (free or paid) or local machine/Raspberry Pi

## License

MIT License - feel free to use and modify for your needs.

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the detailed setup instructions in `SETUP_INSTRUCTIONS.md`
