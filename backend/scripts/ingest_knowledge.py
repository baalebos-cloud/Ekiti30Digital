"""Run from repo root: cd backend && python scripts/ingest_knowledge.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.models.base import SessionLocal
from app.services.knowledge_pipeline import ingest_manifest, local_embed

root = Path(__file__).resolve().parents[2]

# Load the embedding model before opening a database session. This prevents
# hosted PostgreSQL connections from sitting idle while model weights load.
print("Loading embedding model...")
local_embed(["Ask Ekiti embedding warmup"])
print("Embedding model ready.")

with SessionLocal() as db:
    print(json.dumps(
        ingest_manifest(
            root / "13_Knowledge_Base" / "kb_manifest.csv",
            root,
            db,
            local_embed,
        ),
        indent=2,
    ))
