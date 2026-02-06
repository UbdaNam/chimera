#!/usr/bin/env python3
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
SPEC_DIR = os.path.join(ROOT, '.specify', 'specs')

missing = []
checked = 0
for dirpath, dirnames, filenames in os.walk(SPEC_DIR):
    for fn in filenames:
        if fn.endswith('.md'):
            checked += 1
            path = os.path.join(dirpath, fn)
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            if 'specRef' not in text and 'Feature' not in text:
                missing.append(path)

print(f'Checked {checked} spec files.')
if missing:
    print('Spec check failed: the following files do not contain specRef or Feature header:')
    for p in missing:
        print(' -', p)
    sys.exit(2)
print('Spec check passed.')
sys.exit(0)
