"""Ensures `app` is importable when pytest is run from backend/.

Mirrors the same sys.path setup used in alembic/env.py.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
