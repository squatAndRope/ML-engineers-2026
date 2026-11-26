#!/usr/bin/env bash
# Export every rendered slide deck in _site/ to pdf/<deck>.pdf with headless Chrome
# (reveal.js print mode). Run after `quarto render`, then commit pdf/ and publish.
#
#   quarto render && scripts/make_pdfs.sh && quarto publish gh-pages
set -euo pipefail
cd "$(dirname "$0")/.."

CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
PORT="${PORT:-8791}"
mkdir -p pdf
profile="$(mktemp -d)"

python3 -m http.server "$PORT" -d _site >/dev/null 2>&1 &
server=$!
trap 'kill $server 2>/dev/null; rm -rf "$profile"' EXIT
sleep 1

for html in _site/session*.html; do
  name="$(basename "$html" .html)"
  case "$name" in *" "*) continue ;; esac          # skip sync-conflict copies
  # headless Chrome sometimes prints before reveal.js has laid out the deck
  # (a blank one-page PDF), so retry until the PDF has more than one page
  pages=0
  for attempt in $(seq 1 12); do
    rm -rf "$profile"; mkdir -p "$profile"
    "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
      --user-data-dir="$profile" --virtual-time-budget=15000 \
      --run-all-compositor-stages-before-draw \
      --print-to-pdf="pdf/$name.pdf" \
      "http://localhost:$PORT/$name.html?print-pdf" >/dev/null 2>&1 || true
    pages=$(python3 -c "import re,sys; print(len(re.findall(rb'/Type\s*/Page[^s]', open(sys.argv[1],'rb').read())))" "pdf/$name.pdf" 2>/dev/null || echo 0)
    [ "$pages" -gt 1 ] && break
  done
  if [ "$pages" -gt 1 ]; then echo "pdf/$name.pdf  ($pages pages)"; else echo "FAILED: $name" >&2; exit 1; fi
done
