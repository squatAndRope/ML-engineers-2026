# One-step course environment for Windows (PowerShell).
# Usage:  powershell -ExecutionPolicy Bypass -File setup_env.ps1
$ErrorActionPreference = "Stop"
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
Invoke-WebRequest https://squatandrope.github.io/ML-engineers-2026/scripts/requirements.txt -OutFile requirements.txt
pip install -r requirements.txt
python -m ipykernel install --user --name ml-engineers --display-name "Python (ML engineers)"
Write-Host "Done. Activate with:  .\.venv\Scripts\Activate.ps1   then run:  jupyter lab"
