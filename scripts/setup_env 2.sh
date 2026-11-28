#!/usr/bin/env bash
# One-step course environment: Python 3.12 virtual environment with all packages.
# Usage:  bash setup_env.sh        (run in the folder where you keep course work)
set -euo pipefail
PY=${PYTHON:-python3.12}
command -v "$PY" >/dev/null || { echo "Python 3.12 not found. Install it from python.org first."; exit 1; }
"$PY" -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
curl -fsSL https://squatandrope.github.io/ML-engineers-2026/scripts/requirements.txt -o requirements.txt
pip install -r requirements.txt
python -m ipykernel install --user --name ml-engineers --display-name "Python (ML engineers)"
echo "Done. Activate with:  source .venv/bin/activate   then run:  jupyter lab"
