# Changelog

All notable changes to the FS25 Mod Monitor project will be documented in this. file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2024-12-16

### Added

- **Task Runner System** - Professional workflow automation tools
  - `run.py` - Cross-platform Python task runner (works on Windows, Mac, Linux, PythonAnywhere)
  - `Makefile` - Unix-style task runner for Mac/Linux/Git Bash users
  - Quick commands for common operations: `python run.py test`, `python run.py run`, etc.
  - Built-in help system showing all available commands
  - Automated setup wizard for first-time configuration
- **Testing Tools** - Standalone test scripts for verification
  - `test_connection.py` - Tests FTP/SFTP connection independently
  - `test_discord.py` - Tests Discord webhook independently
  - Allows testing individual components before running full monitor
- **Task Runner Documentation** - `TASK_RUNNER.md` with comprehensive guide
  - Platform-specific instructions (Windows, Mac, Linux, PythonAnywhere)
  - Examples for common workflows
  - IDE integration guides (VS Code, PyCharm)
  - Troubleshooting section

### Changed

- Added possible troubleshooting topics associated with testing to Wiki
- Improved .gitignore to allow test scripts while blocking personal test files

### Developer Experience Improvements

- `python run.py setup` - One-command setup (copies config, installs deps)
- `python run.py test` - Runs all tests (FTP + Discord)
- `python run.py test-ftp` - Tests FTP/SFTP connection only
- `python run.py test-discord` - Tests Discord webhook only
- `python run.py run` - Runs the monitor
- `python run.py update` - Pulls latest from GitHub
- `python run.py status` - Shows current configuration
- `python run.py clean` - Removes cache files
- Equivalent `make` commands for Unix users

## [2.0.1] - 2024-12-16

### Fixed
- **Critical:** FTP directory parsing bug that prevented mod scanning
  - Fixed `'file_line' is not defined` error when using FTP connections
  - Improved FTP directory listing collection with proper callback function
  - Enhanced file size parsing to handle various FTP server response formats
  - Added directory filtering to skip folders and only process files
  - Better error handling for malformed FTP directory entries

### Changed
- Refactored FTP directory parsing logic for more robust handling
- Improved file size detection with fallback mechanisms for different server formats
- Added warning messages when file size cannot be determined (uses 0 as fallback)

### Technical Details
- Replaced `client.dir(files.append)` with proper callback function `parse_line()`
- Added directory type checking to skip entries starting with 'd' (directories)
- Implemented intelligent file size parsing that searches multiple columns for numeric values
- Enhanced error messages for debugging FTP listing issues

## [2.0.0] - 2024-12-16

### Added
- **FTP Support** - Full support for FTP and FTPS (FTP with TLS) connections
- **Auto-detection** - Automatically detects whether to use FTP or SFTP based on port and server capabilities
- **Connection flexibility** - Script tries FTPS → FTP → SFTP fallback chain for maximum compatibility
- **Server status summary** - Discord notifications now include total mod count and combined file size at the bottom
- **Enhanced error messages** - Better troubleshooting information when connections fail
- **USE_FTP configuration option** - Optional config parameter to force FTP or SFTP mode

### Changed
- **Breaking:** Renamed configuration variables for clarity (SFTP_* names now apply to both FTP and SFTP)
- **Port handling** - Default port is now 21 for FTP (was 22 for SFTP)
- **Connection method** - Unified connection function that handles both FTP and SFTP protocols
- **File retrieval** - Updated to work with both FTP's `retrbinary` and SFTP's `file` methods
- **Directory listing** - Adapted to parse both FTP LIST format and SFTP attributes

### Fixed
- **G-Portal compatibility** - Now works with G-Portal servers that only support FTP (not SFTP)
- **Authentication errors** - Resolved "Bad authentication type" errors when SSH is not available
- **File size detection** - Improved file size parsing for both FTP and SFTP responses

### Technical Details
- Added `ftplib.FTP` and `ftplib.FTP_TLS` imports for FTP support
- Refactored `connect_sftp()` into modular `connect_ftp()`, `connect_sftp()`, and `connect_server()` functions
- Updated `extract_mod_info()` to accept `conn_type` parameter and handle both protocols
- Modified `get_current_mods()` to parse FTP directory listings and SFTP attributes
- Enhanced `main()` to properly close both FTP and SFTP connections

### Migration Guide
If upgrading from v1.x:

1. **Update config.py:**
   ```python
   # Change this:
   SFTP_PORT = 22
   
   # To this (for FTP):
   SFTP_PORT = 21
   ```

2. **Re-upload script** - Replace old `fs25_mod_monitor.py` with new version

3. **Test connection:**
   ```bash
   python3 fs25_mod_monitor.py
   ```

4. **Verify output** - Should see "Connected to [host] (using FTP)" or similar

## [1.1.0] - 2024-12-16

### Added
- **Server summary section** in Discord notifications showing total mod count and combined file size
- Enhanced Discord embeds with 📊 Current Server Status field

### Changed
- `send_discord_notification()` now accepts `current_mods` parameter to calculate summary stats
- Discord notifications provide more context about overall server state

## [1.0.0] - 2024-12-16

### Added
- Initial release of FS25 Mod Monitor
- SFTP connection support with password authentication
- SSH key authentication support (automatic detection)
- Mod change detection (Added, Removed, Updated)
- ModDesc.xml parsing for mod metadata:
  - Mod title extraction
  - Version tracking
  - Author information
  - File size monitoring
- Discord webhook integration with rich embeds
- JSON state file for tracking changes between runs
- Comprehensive error handling and logging
- Auto-creation of state file on first run

### Features
- **Scheduled monitoring** - Designed to run hourly via cron or PythonAnywhere
- **Silent operation** - Only notifies when changes are detected
- **Secure configuration** - Credentials stored in separate config.py file (gitignored)
- **GitHub-ready** - Full repository structure with documentation

### Documentation
- README.md with feature overview and quick start
- config.example.py as configuration template
- Installation, Deployment, & Troubleshooting Guides are located in Project Wiki

### Security
- Credentials separated from code via config.py
- .gitignore prevents accidental credential commits

---

## Version Numbering

- **Major version (X.0.0)** - Breaking changes, major feature additions
- **Minor version (1.X.0)** - New features, backward compatible
- **Patch version (1.0.X)** - Bug fixes, minor improvements

## Upgrade Notes

### From v1.x to v2.0.0
- **Action required:** Update SFTP_PORT in config.py if using FTP
- **No breaking changes** to Discord webhook or notification format
- **Backward compatible** with existing mod_state.json files
- **No changes required** to scheduled tasks or cron jobs

## Support

For issues or questions about specific versions:
- Check the [GitHub Issues](https://github.com/mattstub/FS25-Mod-Monitor/issues)
- Review relevant documentation in the wiki
- Create a new issue with version information

## Future Roadmap

Anticipated features for upcoming releases:

- [ ] Email notification support as alternative to Discord
- [ ] Mod dependency conflict detection
- [ ] Web dashboard for historical tracking
- [ ] Multiple server monitoring support
- [ ] Slack integration
- [ ] Database backend for long-term history
- [ ] Automated mod pack synchronization

**Note:** Dates reflect development timeline. For production deployments, always use tagged releases from the [Releases page](https://github.com/mattstub/FS25-Mod-Monitor/releases).
