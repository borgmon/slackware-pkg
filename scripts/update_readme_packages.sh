#!/bin/bash
# Group enabled packages by name and merge tags for each, output as markdown table
PACKAGES=$(jq -r '
  [.packages[] | select(.enabled == true)]
  | sort_by(.name)
  | group_by(.name)
  | [
      "| Package | Tags |",
      "|---|---|"
    ] +
    (map(
      "| " + .[0].name + " | " + (
        map(
          if .tag | test("^v[0-9]") then
            (.tag | sub("^v"; ""))
          else
            .tag
          end
        ) | join(", ")
      ) + " |"
    ))
    | join("\n")
' config.json)
awk -v pkgs="$PACKAGES" '
  BEGIN { in_section=0 }
  /<packages>/ { print; print ""; print pkgs; print ""; in_section=1; next }
  /<\/packages>/ { in_section=0 }
  { if (!in_section) print }
' README.md > README.md.tmp && mv README.md.tmp README.md
