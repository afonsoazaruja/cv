#!/bin/sh
# Build and publish to cv.afonsoazaruja.com (same VPS as the site, ssh host "site").
set -e
cd "$(dirname "$0")"
test -z "$(git status --porcelain)" || { echo "✗ Commit your changes first."; exit 1; }
./build.sh
rsync -az --delete dist/ site:/var/www/cv.afonsoazaruja.com/
