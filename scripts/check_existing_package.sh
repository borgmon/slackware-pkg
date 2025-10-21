#!/bin/bash
PACKAGE_NAME="$1"
PACKAGE_VERSION="$2"
PACKAGE_BUILD="$3"
PACKAGE_FILE="${PACKAGE_NAME}-${PACKAGE_VERSION}-x86_64-${PACKAGE_BUILD}.tgz"
# Fetch the build branch to check for existing packages
git fetch origin build:build 2>/dev/null || echo "Build branch does not exist yet"
if git ls-tree -r build --name-only 2>/dev/null | grep -q "slackware64-current/${PACKAGE_NAME}/$PACKAGE_FILE"; then
  echo "skip=true" >> "$4"
  echo "✓ Package $PACKAGE_FILE already exists in build branch - skipping build"
else
  echo "skip=false" >> "$4"
  echo "→ Package $PACKAGE_FILE not found - will build"
fi
