#!/usr/bin/env bash
# Substitute placeholders inside a freshly-scaffolded project.
#
# Usage:
#   ./substitute-placeholders.sh <target_dir> <project_name> <project_slug> <first_date> <owner> <author>
#
# Example:
#   ./substitute-placeholders.sh ~/code-projects/acme-bookstore \
#     "Acme Bookstore" acme-bookstore 2026-05-20 "Dave Hajdu" "Dave Hajdu"
#
# Does NOT rename `PH-` filenames — those stay so the operator renames them deliberately.

set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <target_dir> <project_name> <project_slug> [first_date] [owner] [author]"
  exit 1
fi

TARGET="$1"
PROJECT_NAME="$2"
PROJECT_SLUG="$3"
FIRST_DATE="${4:-$(date +%Y-%m-%d)}"
OWNER="${5:-Owner}"
AUTHOR="${6:-$OWNER}"

if [ ! -d "$TARGET" ]; then
  echo "❌ Target directory not found: $TARGET"
  exit 1
fi

echo "→ Substituting placeholders in $TARGET"
echo "   Project Name : $PROJECT_NAME"
echo "   Slug         : $PROJECT_SLUG"
echo "   First date   : $FIRST_DATE"
echo "   Owner        : $OWNER"
echo "   Author       : $AUTHOR"

# Find every text file (skip binary, .git, node_modules)
FILES=$(find "$TARGET" -type f \
  -not -path '*/.git/*' \
  -not -path '*/node_modules/*' \
  -not -path '*/.next/*' \
  \( -name '*.md' -o -name '*.html' -o -name '*.json' \
     -o -name '*.txt' -o -name '*.example' -o -name '.gitignore' \
     -o -name '.env*' -o -name 'CLAUDE.md' -o -name 'README.md' \))

# Use perl for portable in-place edit (sed -i differs on macOS vs Linux)
for f in $FILES; do
  perl -i -pe "
    s/\Q{Project Name}\E/$PROJECT_NAME/g;
    s/\Q{project-slug}\E/$PROJECT_SLUG/g;
    s/\QPH-author\E/$AUTHOR/g;
    s/\QPH-Author\E/$AUTHOR/g;
  " "$f"
done

# Date substitution: ONLY in folders where YYYY-MM-DD is meant as a real date
DATE_SCOPES=(
  "$TARGET/content/topics"
  "$TARGET/standup/briefings"
  "$TARGET/emails/drafts"
  "$TARGET/docs/engineering/changes"
)
for scope in "${DATE_SCOPES[@]}"; do
  [ -d "$scope" ] || continue
  find "$scope" -type f \
    \( -name '*.md' -o -name '*.html' -o -name '*.json' \) \
    -exec perl -i -pe "s/\QYYYY-MM-DD\E/$FIRST_DATE/g" {} +
done

echo "✅ Placeholders substituted."
echo "   Note: PH- prefixed FILENAMES were not renamed. Rename them deliberately on first use."
