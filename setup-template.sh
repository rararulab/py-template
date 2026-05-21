#!/usr/bin/env bash
# Rename template placeholders in-place. Run once after cloning.
#
# Usage:
#   ./setup-template.sh <project-name> <package-name> "<description>" "<author>" "<email>" "<github-org>"
#
# Example:
#   ./setup-template.sh foobar foobar "A tiny tool that does X." "Ada Lovelace" "ada@example.com" "myorg"
#
# Notes:
#   - project-name is what users `pip install` (kebab-case OK).
#   - package-name is the Python import name (snake_case, no dashes).
#   - After running, this script deletes itself.

set -euo pipefail

if [ "$#" -ne 6 ]; then
    sed -n '3,15p' "$0"
    exit 2
fi

PROJECT_NAME="$1"
PKG_NAME="$2"
DESCRIPTION="$3"
AUTHOR_NAME="$4"
AUTHOR_EMAIL="$5"
GITHUB_ORG="$6"

# Reject bad package names early. Python identifiers only.
if ! [[ "$PKG_NAME" =~ ^[a-z_][a-z0-9_]*$ ]]; then
    echo "error: package name '$PKG_NAME' must be snake_case (lowercase, underscores, no dashes)" >&2
    exit 2
fi

echo "==> Renaming src/__pkg__/ -> src/$PKG_NAME/"
git mv src/__pkg__ "src/$PKG_NAME" 2>/dev/null || mv src/__pkg__ "src/$PKG_NAME"

# Files to rewrite. Keep this list explicit so we never sed inside .venv/ or .git/.
FILES=(
    pyproject.toml
    justfile
    README.md
    AGENT.md
    CLAUDE.md
    CHANGELOG.md
    mkdocs.yml
    .release-please-config.json
    docs/index.md
    docs/api.md
    docs/guide/install.md
    docs/guide/usage.md
    docs/dev/contributing.md
    docs/dev/release.md
    "src/$PKG_NAME/__init__.py"
    "src/$PKG_NAME/cli.py"
    "src/$PKG_NAME/core.py"
    tests/test_core.py
    tests/test_cli.py
)

echo "==> Substituting placeholders"
# macOS sed needs '' after -i; GNU sed does not. Use a portable approach.
for f in "${FILES[@]}"; do
    [ -f "$f" ] || continue
    # Order matters: replace __pkg__ first so it doesn't clobber other tokens.
    python3 - "$f" <<EOF
import sys
from pathlib import Path
p = Path(sys.argv[1])
text = p.read_text()
subs = {
    "__pkg__": "$PKG_NAME",
    "__PKG__": "$PKG_NAME",
    "__PROJECT_NAME__": "$PROJECT_NAME",
    "__PROJECT_DESCRIPTION__": "$DESCRIPTION",
    "__AUTHOR_NAME__": "$AUTHOR_NAME",
    "__AUTHOR_EMAIL__": "$AUTHOR_EMAIL",
    "__GITHUB_ORG__": "$GITHUB_ORG",
}
for k, v in subs.items():
    text = text.replace(k, v)
p.write_text(text)
EOF
done

echo "==> Removing setup script"
rm -- "$0"

echo ""
echo "✅ Template initialised."
echo "Next:"
echo "  just install   # uv sync + pre-commit install"
echo "  just check     # ruff + mypy + pyright"
echo "  just test      # pytest + coverage gates"
