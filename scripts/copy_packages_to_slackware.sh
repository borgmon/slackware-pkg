#!/bin/bash
echo "Copying packages from artifacts..."
mkdir -p slackware64-current
if [ -d artifacts ]; then
  for pkg_dir in artifacts/package-*; do
    if [ -d "$pkg_dir" ]; then
      pkg_name=$(basename "$pkg_dir" | sed 's/^package-//')
      echo "Copying $pkg_name..."
      mkdir -p "slackware64-current/$pkg_name"
      cp -r "$pkg_dir"/* "slackware64-current/$pkg_name/"
    fi
  done
fi
echo "Package directory structure:"
ls -lR slackware64-current/
