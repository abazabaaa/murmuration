#!/usr/bin/env python3
"""Freeze an allowlisted, runnable app and evidence; never mutate the source."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--historical', type=Path, help='optional earlier profile artifact directory')
args = parser.parse_args()
source, output = args.source.resolve(), args.output.resolve()
if output.exists() or output.with_suffix('.tar.gz').exists():
    parser.error('output already exists; choose a fresh directory')
if source == output or source in output.parents:
    parser.error('output must be outside the source tree')
sha = lambda file: hashlib.sha256(file.read_bytes()).hexdigest()
product_before = {p: sha(source / p) for p in ['murmuration.html', 'motion/motion.js', 'motion/motion-data.js']}
git = lambda *cmd: subprocess.check_output(['git', *cmd], cwd=source, text=True)
state = {'createdUTC': datetime.now(timezone.utc).isoformat(), 'source': str(source),
         'head': git('rev-parse', 'HEAD').strip(), 'branch': git('branch', '--show-current').strip(),
         'dirtyStatus': git('status', '--short'), 'platform': platform.platform(),
         'architecture': platform.machine(), 'node': subprocess.check_output(['node', '--version'], text=True).strip(),
         'runtimeHashes': product_before,
         'scope': 'runtime, simulator, plans, reference manifests, motion rig and source inputs; not a full repository clone',
         'excluded': ['.git', 'node_modules', '.claude', 'blender-mcp', 'sim-output',
                      'species render/photo trees', 'full species .blend scenes', 'external research PDFs'],
         'nativeProvider': 'optional external @napi-rs/canvas; not bundled; native results used version 0.1.100',
         'browserFPS': 'unobserved; managed security-policy verification blocked Chrome control'}
output.mkdir(parents=True)

def copy(relative, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / relative, destination)

root_files = ['murmuration.html', 'motion-lab.html', 'murmuration-sky.jpg',
              'murmuration-check.js', 'murmuration-falcon.js', 'README.md', 'CREDITS.md', 'LICENSE', '.gitignore']
for name in root_files:
    copy(name, output / 'app' / name)
for tree in ['motion', 'sim', 'docs', 'starling/blender', 'falcon/blender', 'starling/refs', 'falcon/refs']:
    for file in sorted((source / tree).rglob('*')):
        if file.is_file() and '__pycache__' not in file.parts and file.suffix in {'.js', '.json', '.md', '.py', '.blend', '.txt', '.csv'}:
            copy(file.relative_to(source), output / 'app' / file.relative_to(source))
for name in ['starling/README.md', 'falcon/README.md']:
    copy(name, output / 'app' / name)

# Scripts resolve relative to HTML, so a lone HTML is not a runnable reference.
runtime = ['murmuration.html', 'motion-lab.html', 'murmuration-sky.jpg', 'motion/motion.js', 'motion/motion-data.js']
for name in runtime:
    copy(name, output / 'baseline' / name)
copy('docs/optimization/HANDOFF.md', output / 'START_HERE.md')
copy('docs/optimization/tools/verify-package.py', output / 'verify-package.py')
copy('docs/optimization/tools/glyph-compare.js', output / 'glyph-compare.js')
(output / 'SOURCE_STATE.json').write_text(json.dumps(state, indent=2) + '\n')
(output / 'TRACKED_CHANGES.patch').write_text(git('diff', '--binary'))

oldmain = output / 'historical' / 'main-0d3078f'
oldmain.mkdir(parents=True)
(oldmain / 'murmuration.html').write_text(git('show', '0d3078f:murmuration.html'))
copy('murmuration-sky.jpg', oldmain / 'murmuration-sky.jpg')
if args.historical:
    earlier = args.historical.resolve()
    for name in ['before-native.json', 'before-stub.json', 'before-legacy.json', 'boundary-native.json',
                 'per-bird-native.json', 'independent-glyph-result.json', 'independent-glyph-8x-result.json']:
        file = earlier / name
        if file.is_file():
            destination = output / 'historical' / name
            shutil.copy2(file, destination)
    if (earlier / 'baseline/murmuration.html').is_file():
        for name in ['murmuration.html', 'motion-lab.html', 'motion/motion.js', 'motion/motion-data.js']:
            destination = output / 'historical/pre-contour' / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(earlier / 'baseline' / name, destination)
        copy('murmuration-sky.jpg', output / 'historical/pre-contour/murmuration-sky.jpg')

if any(sha(source / p) != digest for p, digest in product_before.items()):
    raise RuntimeError('source runtime changed while freezing; do not use this package')
files = [{'path': str(file.relative_to(output)), 'bytes': file.stat().st_size, 'sha256': sha(file)}
         for file in sorted(output.rglob('*')) if file.is_file()]
manifest = {'schema': 1, 'baselineHTML': product_before['murmuration.html'], 'files': files}
(output / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
subprocess.run(['python3', str(output / 'verify-package.py'), str(output)], check=True)
archive = output.with_suffix('.tar.gz')
with tarfile.open(archive, 'w:gz') as tar:
    tar.add(output, arcname=output.name)
print(json.dumps({'directory': str(output), 'archive': str(archive), 'archiveSHA256': sha(archive),
                  'files': len(files), 'bytes': sum(item['bytes'] for item in files)}))
