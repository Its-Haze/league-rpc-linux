#!/bin/bash

# Configurations
REPO="Its-Haze/league-rpc-linux"
EXECUTABLE="league_rpc_linux"

# Use XDG_BIN_HOME for the executable, defaulting to ~/.local/bin if not set
XDG_BIN_HOME=${XDG_BIN_HOME:-$HOME/.local/bin}
EXECUTABLE_PATH="$XDG_BIN_HOME/$EXECUTABLE"

# Default to HOME if XDG_CACHE_HOME is not set for logs
XDG_CACHE_HOME=${XDG_CACHE_HOME:-$HOME/.cache}
LOG_DIR="$XDG_CACHE_HOME/league-rpc-linux"
LOG_FILE="$LOG_DIR/update_log.txt"

AUTO_INSTALL=true # Set this to (true) to always install/update the latest version.

# Create the installation and log directories if they don't exist
mkdir -p "$XDG_BIN_HOME"
mkdir -p "$LOG_DIR"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check for required programs: curl and grep
for required_command in curl grep; do
    if ! command -v $required_command &>/dev/null; then
        log_message "Error: $required_command is not installed. Please install it and try again."
        exit 1
    fi
done

# Function to download and update the executable
update_executable() {
    log_message "Installing the executable..."
    DOWNLOAD_URL=$(curl -s "https://api.github.com/repos/$REPO/releases/latest" |
        grep "\"browser_download_url\": \".*$EXECUTABLE\"" |
        cut -d '"' -f 4)

    if [ -z "$DOWNLOAD_URL" ]; then
        log_message "Failed to fetch release info."
        exit 1
    fi

    log_message "Downloading from $DOWNLOAD_URL"
    if curl -Ls "$DOWNLOAD_URL" -o "$EXECUTABLE_PATH"; then
        chmod +x "$EXECUTABLE_PATH" || log_message "Failed to set executable permission."
        log_message "Update successful."
    else
        log_message "Failed to download the executable."
        exit 1
    fi
}

# Process command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
    --auto-install)
        AUTO_INSTALL=true
        shift
        ;;
    --add-process)
      if [ -n "$2" ]; then
        process="$2"
        log_message "Selected process: $process"
        shift 2
      else
        log_message "Error: Argument required for --add-process" 
        exit 1
      fi
      ;;
    *)
        log_message "Unknown option: $1"
        exit 1
        ;;
    esac
done

# Perform auto-install if enabled
if [[ "$AUTO_INSTALL" == true ]]; then
    update_executable
fi

# Check if the executable exists and is executable
if [[ ! -x "$EXECUTABLE_PATH" ]]; then
    log_message "ERROR: Executable not found at $EXECUTABLE_PATH"
    log_message "INFO: If you want to quickly fetch the latest version, use --auto-install."
    exit 1
fi

# Execute the program
log_message "Executing the program..."
if [ -z "$process" ]; then
    log_message "using custom discord process: $process"
    exec exec "$EXECUTABLE_PATH" --wait-for-league -1 --wait-for-discord -1 --add-process "$process" 
else
    log_message "using default discord process"
    exec "$EXECUTABLE_PATH" --wait-for-league -1 --wait-for-discord -1
fi
