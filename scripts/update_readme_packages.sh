#!/bin/bash
PACKAGES=$(jq -r '.packages[] | select(.enabled == true) | "- "+.name+": v"+.version' config.json)
awk -v pkgs="$PACKAGES" '
  BEGIN { in_section=0 }
  /<packages>/ { print; print ""; print pkgs; print ""; in_section=1; next }
  /<\/packages>/ { in_section=0 }
  { if (!in_section) print }
' README.md > README.md.tmp && mv README.md.tmp README.md
