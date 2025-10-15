# 현재 스크립트의 디렉터리 기준으로 가상환경 python 찾기
$base = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvPython = Join-Path $base ".venv\Scripts\python.exe"
$appPath = Join-Path $base "app.py"
$pidPath = Join-Path $base "app.pid"

# 에러 처리를 위한 try-catch 블록 시작
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
        } catch {
            Write-Warning "Failed to remove previous PID file: $($_.Exception.Message)"
        }
    }

    Write-Host "Starting server..."

    # Start process and verify success
    $proc = Start-Process -FilePath $venvPython -ArgumentList $appPath -WindowStyle Hidden -PassThru -ErrorAction Stop

    # Verify process started successfully
    if (-not $proc -or $proc.HasExited) {
        throw "Failed to start the process."
    }

    # Save process ID to PID file
    try {
        $proc.Id | Out-File -FilePath $pidPath -Encoding ascii -ErrorAction Stop
        Write-Host "Server started successfully. (PID: $($proc.Id))"
        Write-Host "PID file: $pidPath"
    } catch {
        # Terminate process if PID file write fails
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        throw "Failed to save PID file: $($_.Exception.Message)"
    }

} catch {
    # Handle all errors here
    Write-Error "Server startup failed: $($_.Exception.Message)"
    exit 1
}
