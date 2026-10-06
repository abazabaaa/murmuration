#!/usr/bin/env python3
"""Verify a frozen handoff before working on a separate candidate copy."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
manifest = json.loads((root / 'MANIFEST.json').read_text())
errors = []
for item in manifest['files']:
    file = root / item['path']
    if not file.is_file():
        errors.append(f"missing: {item['path']}")
    elif hashlib.sha256(file.read_bytes()).hexdigest() != item['sha256']:
        errors.append(f"changed: {item['path']}")
if errors:
    print('\n'.join(errors), file=sys.stderr)
    sys.exit(1)
print(json.dumps({'status': 'matched', 'files': len(manifest['files']),
                  'baselineHTML': manifest['baselineHTML'], 'root': str(root)}))
