#!/bin/sh
# Build the CV into dist/: the PDF (RenderCV) and the web page (build_html.py).
set -e
cd "$(dirname "$0")"
rm -rf dist
uvx --from 'rendercv[full]==2.8' rendercv render cv.yaml --dont-generate-html --dont-generate-markdown
rm -f dist/*.typ
uv run --no-project --with pyyaml python build_html.py
