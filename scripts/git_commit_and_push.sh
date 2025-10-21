#!/bin/bash
# Usage: git_commit_and_push.sh <file_or_dir_to_add> <commit_message>
set -e
FILE_TO_ADD="$1"
COMMIT_MSG="$2"

git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
git add "$FILE_TO_ADD"
if git diff --cached --quiet; then
  echo "No changes to commit for $FILE_TO_ADD"
else
  git commit -m "$COMMIT_MSG"
  git push origin
fi
