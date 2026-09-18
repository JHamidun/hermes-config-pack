# Wrapper: finds a real Python and hands over to install.py.
# All flags pass through: -DryRun becomes --dry-run, and so on.
#
#   powershell -ExecutionPolicy Bypass -File .\install-hermes.ps1
#   powershell -ExecutionPolicy Bypass -File .\install-hermes.ps1 --dry-run

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

function Find-Python {
    foreach ($name in @('python', 'python3', 'py')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        # The Microsoft Store stub is on PATH by default and does nothing but
        # open the Store — running it looks like a hung install.
        if ($cmd.Source -like '*WindowsApps*') { continue }
        $v = & $cmd.Source -c "import sys; print(sys.version_info[:2] >= (3, 9))" 2>$null
        if ($v -eq 'True') { return $cmd.Source }
    }
    return $null
}

$python = Find-Python
if (-not $python) {
    Write-Host "Python 3.9+ not found. Install it from python.org (not the Store stub) and run again."
    exit 1
}

& $python (Join-Path $here 'install.py') @args
exit $LASTEXITCODE
