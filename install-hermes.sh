#!/usr/bin/env sh
# Wrapper: finds a Python 3.9+ and hands over to install.py. Flags pass through.
#
#   ./install-hermes.sh --dry-run
set -eu

here=$(cd "$(dirname "$0")" && pwd)

for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3, 9) else 1)' 2>/dev/null; then
            exec "$candidate" "$here/install.py" "$@"
        fi
    fi
done

echo "Python 3.9+ not found on PATH." >&2
exit 1
