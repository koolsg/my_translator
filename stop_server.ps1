# Stop the translation server process
# This script safely stops the running Flask application server by:
# 1. Reading and validating the PID from app.pid file
# 2. Checking if the process is actually running
# 3. Stopping the process and cleaning up the PID file

# Get script directory and construct PID file path
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$pidPath = Join-Path $scriptDir "app.pid"

# Helper function: Validates PID file and returns process ID if valid
# Returns $null if file doesn't exist, is empty, or contains invalid PID
function Test-PidFile {
    param([string]$Path)

    # Check if PID file exists
    if (-not (Test-Path $Path)) { return $null }

    try {
        # Read file content and trim whitespace
        $content = Get-Content $Path -ErrorAction Stop
        $processId = $content.Trim()

        # Validate that content is not empty and is a valid integer
        if ([string]::IsNullOrEmpty($processId) -or -not [int]::TryParse($processId, [ref]$null)) {
            return $null
        }

        return [int]$processId

    } catch {
        # Return null on any error (file access issues, etc.)
        return $null
    }
}

# Helper function: Stops the server process and cleans up PID file
# Exits with error code 1 if stopping fails
function Stop-ServerProcess {
    param([int]$ProcessId, [string]$PidFilePath)

    try {
        # Forcefully stop the process
        Stop-Process -Id $ProcessId -Force -ErrorAction Stop

        # Clean up PID file after successful stop
        Remove-Item $PidFilePath -Force -ErrorAction SilentlyContinue

        Write-Host "Server stopped successfully."

    } catch {
        # Exit with error if process cannot be stopped
        Write-Error "Failed to stop process with PID $ProcessId`: $($_.Exception.Message)"
        exit 1
    }
}

# Main execution logic
# Step 1: Try to get valid process ID from PID file
$processId = Test-PidFile -Path $pidPath

# Step 2: Exit gracefully if no valid PID file found
if ($null -eq $processId) {
    Write-Host "No valid PID file found. Server may not be running."
    exit 0
}

# Step 3: Check if process with that ID is actually running
if (-not (Get-Process -Id $processId -ErrorAction SilentlyContinue)) {
    Write-Warning "Process with PID $processId not found. It may have already stopped."
    # Clean up stale PID file
    Remove-Item $pidPath -Force -ErrorAction SilentlyContinue
    exit 0
}

# Step 4: Stop the running server process
Write-Host "Stopping server process (PID: $processId)..."
Stop-ServerProcess -ProcessId $processId -PidFilePath $pidPath
