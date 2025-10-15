# Start the translation server in background mode
# This script launches the Flask application using pythonw.exe for windowless execution
# and saves the process ID for later management

# Get script directory and set up environment
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location -Path $scriptDir  # Fix current directory to avoid shell startup influences

# Construct file paths
$venvPython = Join-Path $scriptDir ".venv\Scripts\pythonw.exe"  # Use standard venv path for consistency
$appPath = Join-Path $scriptDir "app.py"
$pidPath = Join-Path $scriptDir "app.pid"

try {
    # Check if virtual environment Python executable exists
    if (-not (Test-Path $venvPython)) {
        throw "Virtual environment Python not found: $venvPython`nPlease ensure venv is properly set up."
    }

    # Check if application file exists
    if (-not (Test-Path $appPath)) {
        throw "Application file not found: $appPath"
    }

    # Clean up previous PID file if it exists
    if (Test-Path $pidPath) {
        try {
            Remove-Item $pidPath -Force
            Write-Host "Previous PID file cleaned up."
        }
        catch {
            Write-Warning "Failed to remove previous PID file: $($_.Exception.Message)"
        }
    }

    Write-Host "Starting server in background mode..."

    # Configure ProcessStartInfo for silent background execution
    # pythonw.exe runs without console window, ProcessStartInfo prevents PowerShell window flash
    $processStartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processStartInfo.FileName = $venvPython
    $processStartInfo.Arguments = "`"$appPath`""
    $processStartInfo.WorkingDirectory = $scriptDir
    $processStartInfo.CreateNoWindow = $true
    $processStartInfo.UseShellExecute = $false

    # Start the process
    $process = [System.Diagnostics.Process]::Start($processStartInfo)

    # Verify process started successfully
    if (-not $process -or $process.HasExited) {
        throw "Failed to start the process."
    }

    # Save process ID to PID file
    $process.Id | Out-File -FilePath $pidPath -Encoding ascii -ErrorAction Stop

    Write-Host "Server started successfully. (PID: $($process.Id))"
    Write-Host "PID file: $pidPath"
    Write-Host "Server is running in background. Use stop_server-2.ps1 to stop it."

}
catch {
    Write-Error "Server startup failed: $($_.Exception.Message)"
    exit 1
}
