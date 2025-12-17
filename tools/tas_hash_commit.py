#!/usr/bin/env python3
"""
TAS_DNA Provenance Hasher (v1.0)
Authority: True Alpha Spiral / Sovereign Ethical Singularity
Purpose:   Auto-computes SHA3-512 checksums for TAS artifacts and injects them
           into the [PLACEHOLDER] fields before version control commit.

Usage:     python3 tas_hash_commit.py [directory_path]
"""

import os
import sys
import hashlib
import re
import json
import time
from pathlib import Path

# --- Configuration ---
PLACEHOLDER_TAG = "[PLACEHOLDER_HASH_TBD_ON_COMMIT]"
HASH_ALGO = "sha3_512"
MANIFEST_FILE = "TAS_COMMIT_MANIFEST.json"

# File extensions to scan
TARGET_EXTENSIONS = {".tex", ".md", ".json", ".yaml", ".py"}

def compute_hash(content_bytes: bytes) -> str:
    """Computes the SHA3-512 hash of the content."""
    h = hashlib.sha3_512()
    h.update(content_bytes)
    return h.hexdigest()

def process_file(file_path: Path) -> dict:
    """
    Reads a file, calculates its hash (treating the placeholder as a null value
    to avoid circular dependency), and injects the hash back into the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return None  # Skip binary files

    if PLACEHOLDER_TAG not in content:
        return None

    print(f"[*] Processing artifact: {file_path.name}")

    # 1. Normalize content for hashing
    # We replace the placeholder with a fixed string "TAS_NULL_HASH"
    # to create a stable pre-image for the hash function.
    normalized_content = content.replace(PLACEHOLDER_TAG, "TAS_NULL_HASH_PREIMAGE")

    # 2. Compute the Sovereign Hash
    artifact_hash = compute_hash(normalized_content.encode('utf-8'))

    # 3. Inject the Hash
    # We format it to fit strictly into the LaTeX/Markdown structure
    new_content = content.replace(PLACEHOLDER_TAG, artifact_hash)

    # 4. Write back to disk
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"    -> Sealed with SHA3-512: {artifact_hash[:16]}...")

    return {
        "file_name": file_path.name,
        "path": str(file_path),
        "hash": artifact_hash,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

def generate_manifest(records: list, root_dir: Path):
    """
    Creates a JSON manifest of all sealed artifacts in this batch.
    """
    manifest = {
        "event": "TAS_ARTIFACT_SEALING",
        "authority": "TAS_DNA_ENGINE",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "artifact_count": len(records),
        "artifacts": records,
        "batch_hash": ""  # To be computed
    }

    # Compute batch hash (Merkle root equivalent)
    manifest_str = json.dumps(manifest['artifacts'], sort_keys=True)
    manifest['batch_hash'] = compute_hash(manifest_str.encode('utf-8'))

    manifest_path = root_dir / MANIFEST_FILE
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n[+] Manifest generated: {manifest_path}")
    print(f"    Batch Root Hash: {manifest['batch_hash'][:16]}...")

def main():
    root_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

    if not root_path.exists():
        print(f"Error: Path {root_path} does not exist.")
        sys.exit(1)

    print(f"--- TAS-W Provenance Hasher initialized on {root_path} ---")

    sealed_records = []

    # Recursive scan
    for file_path in root_path.rglob("*"):
        if file_path.suffix in TARGET_EXTENSIONS and file_path.name != "tas_hash_commit.py":
            result = process_file(file_path)
            if result:
                sealed_records.append(result)

    if sealed_records:
        generate_manifest(sealed_records, root_path)
        print("\n--- Sealing Complete. Artifacts ready for ITL Ingestion. ---")
    else:
        print("\nNo unsealed artifacts (placeholders) found.")

if __name__ == "__main__":
    main()
