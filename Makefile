# FS25 Mod Monitor - Makefile
# Provides convenient shortcuts for common tasks
# Usage: make <command>

.PHONY: help install test test-ftp test-discord run setup clean update

# Default target - show help
help:
	@echo "FS25 Mod Monitor - Available Commands"
	@echo "======================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install       - Install Python dependencies"
	@echo "  make setup         - First-time setup (copy config, install deps)"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run all tests"
	@echo "  make test-ftp      - Test FTP/SFTP connection only"
	@echo "  make test-discord  - Test Discord webhook only"
	@echo ""
	@echo "Running:"
	@echo "  make run           - Run the mod monitor once"
	@echo "  make run-verbose   - Run with detailed output"
	@echo ""
	@echo "Maintenance:"
	@echo "  make update        - Pull latest changes from GitHub"
	@echo "  make clean         - Remove cache files and logs"
	@echo "  make status        - Show current configuration status"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip3 install -r requirements.txt
	@echo "✓ Dependencies installed!"

# First-time setup
setup:
	@echo "Setting up FS25 Mod Monitor..."
	@if [ ! -f config.py ]; then \
		cp config.example.py config.py; \
		echo "✓ Created config.py from template"; \
		echo "⚠️  Please edit config.py with your credentials!"; \
	else \
		echo "✓ config.py already exists"; \
	fi
	@$(MAKE) install
	@echo ""
	@echo "✓ Setup complete!"
	@echo "Next steps:"
	@echo "  1. Edit config.py with your server credentials"
	@echo "  2. Run 'make test' to verify connections"
	@echo "  3. Run 'make run' to start monitoring"

# Run all tests
test:
	@echo "Running all tests..."
	@echo ""
	@$(MAKE) test-ftp
	@echo ""
	@$(MAKE) test-discord
	@echo ""
	@echo "✓ All tests complete!"

# Test FTP connection
test-ftp:
	@echo "Testing FTP/SFTP connection..."
	python3 test_connection.py

# Test Discord webhook
test-discord:
	@echo "Testing Discord webhook..."
	python3 test_discord.py

# Run the monitor
run:
	@echo "Running FS25 Mod Monitor..."
	python3 fs25_mod_monitor.py

# Run with verbose output
run-verbose:
	@echo "Running FS25 Mod Monitor (verbose)..."
	python3 -u fs25_mod_monitor.py

# Update from GitHub
update:
	@echo "Pulling latest changes from GitHub..."
	git pull origin main
	@echo "✓ Updated to latest version!"
	@echo "Run 'make run' to use the updated version"

# Clean cache and temporary files
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.log" -delete 2>/dev/null || true
	@echo "✓ Cleanup complete!"

# Show configuration status
status:
	@echo "FS25 Mod Monitor - Configuration Status"
	@echo "========================================"
	@echo ""
	@if [ -f config.py ]; then \
		echo "✓ config.py exists"; \
		python3 -c "import config; print(f'  Host: {config.SFTP_HOST}'); print(f'  Port: {config.SFTP_PORT}'); print(f'  Path: {config.SFTP_MODS_PATH}')"; \
	else \
		echo "✗ config.py not found - run 'make setup'"; \
	fi
	@echo ""
	@if [ -f mod_state.json ]; then \
		echo "✓ mod_state.json exists (monitoring active)"; \
		python3 -c "import json; data=json.load(open('mod_state.json')); print(f'  Tracking {len(data)} mods')"; \
	else \
		echo "ℹ️  mod_state.json not found (first run pending)"; \
	fi
	@echo ""
