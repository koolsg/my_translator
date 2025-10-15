# Stop the translation server process and its child processes
# This script safely stops the Flask application and any child processes by:
# 1. Reading and validating the PID from app.pid file
# 2. Finding and stopping all child processes recursively
# 3. Stopping the main process
# 4. Cleaning up the PID file

# Get script directory and PID file path
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$pidPath = Join-Path $scriptDir "app.pid"

# Helper function: Validates PID file and returns process ID
# Returns $null if file doesn't exist, is empty, or contains invalid PID
function Test-PidFile {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return $null }
    try {
        $content = Get-Content $Path -ErrorAction Stop
        $processId = $content.Trim()
        if ([string]::IsNullOrEmpty($processId) -or -not [int]::TryParse($processId, [ref]$null)) {
            return $null
        }
        return [int]$processId
    }
    catch { return $null }
}

# Helper function: Gets all child processes recursively
function Get-ChildProcesses {
    param([int]$ParentId)
    $childProcesses = @()

    try {
        $children = Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $ParentId }
        foreach ($child in $children) {
            # Add child processes recursively first
            $childProcesses += Get-ChildProcesses -ParentId $child.ProcessId
            # Add current child
            $childProcesses += $child
        }
    }
    catch {
        Write-Warning "Failed to query child processes for PID $ParentId`: $($_.Exception.Message)"
    }

    return $childProcesses
}

# Helper function: Stops a list of processes
function Stop-Processes {
    param([array]$Processes, [string]$Type)
    foreach ($proc in $Processes) {
        try {
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
            Write-Host "Stopped $Type process: $($proc.ProcessId) $($proc.Name)"
        }
        catch {
            Write-Warning "Failed to stop $Type process $($proc.ProcessId) $($proc.Name)`: $($_.Exception.Message)"
        }
    }
}

# Main execution logic
# Step 1: Get valid process ID from PID file
$processId = Test-PidFile -Path $pidPath

if ($null -eq $processId) {
    Write-Host "No valid PID file found. Server may not be running."
    exit 0
}

# Step 2: Check if main process is running
$mainProcess = Get-Process -Id $processId -ErrorAction SilentlyContinue
if (-not $mainProcess) {
    Write-Warning "Process with PID $processId not found. It may have already stopped."
    Remove-Item $pidPath -Force -ErrorAction SilentlyContinue
    exit 0
}

Write-Host "Stopping server and child processes for PID: $processId..."

# Step 3: Get all child processes
$childProcesses = Get-ChildProcesses -ParentId $processId
Write-Host "Found $($childProcesses.Count) child processes to stop."

# Step 4: Stop child processes first (in reverse order for proper cleanup)
if ($childProcesses.Count -gt 0) {
    Stop-Processes -Processes $childProcesses -Type "child"
}

# Step 5: Stop main process
try {
    Stop-Process -Id $processId -Force -ErrorAction Stop
    Write-Host "Stopped main process: $processId $($mainProcess.Name)"
}
catch {
    Write-Error "Failed to stop main process $processId`: $($_.Exception.Message)"
    exit 1
}

# Step 6: Clean up PID file
Remove-Item $pidPath -Force -ErrorAction SilentlyContinue
Write-Host "Server and all child processes stopped successfully."
