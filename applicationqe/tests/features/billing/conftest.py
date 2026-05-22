"""
Billing Feature Root — conftest.py

Minimal conftest at the billing feature root.
All tests under tests/features/billing/ inherit:
  - sys.path augmentation so 'pages.*' and 'tests.*' absolute imports resolve.
  - The shared BDD hooks from tests.fixtures.hooks_fixtures.
"""

import sys
from pathlib import Path

# Ensure the repo root (applicationqe/) is always on sys.path for absolute imports.
_REPO_ROOT = Path(__file__).resolve().parents[3]  # applicationqe/
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
