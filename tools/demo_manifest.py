"""Hash the offline display artifact separately from the mathematical certificate."""

import hashlib
import json
from pathlib import Path

ASSETS = ("README.md", "app.js", "data.js", "data.json", "index.html", "style.css")


def build_manifest(directory: Path, replacements: dict[str, bytes] | None = None) -> dict:
    """Describe exactly the six local assets; exclude the manifest itself."""
    replacements = replacements or {}
    if not set(replacements).issubset(ASSETS):
        raise ValueError("display-manifest replacements must name a known asset")
    assets = {
        name: replacements[name] if name in replacements else (directory / name).read_bytes()
        for name in ASSETS
    }
    display = json.loads(assets["data.json"])
    return {
        "schema_version": 1,
        "revision_kind": "offline_display_revision",
        "scope": "Source hashes for the offline demonstration, not a mathematical certificate.",
        "certificate_sources": {
            "original-verify": display["source"]["certificate_sha256"],
            "long-exposure-v1": display["profiles"]["long-exposure-v1"]["source"][
                "certificate_sha256"
            ],
            "package_manifest_sha256": display["source"]["package_manifest_sha256"],
        },
        "files": [
            {"path": name, "sha256": hashlib.sha256(assets[name]).hexdigest()} for name in ASSETS
        ],
    }


def check_manifest(directory: Path) -> None:
    """Reject changed or missing assets before building the published archive."""
    path = directory / "SOURCE_MANIFEST.json"
    if not path.is_file() or json.loads(path.read_text("utf-8")) != build_manifest(directory):
        raise RuntimeError(
            "offline-demo manifest is absent or stale; review changes and regenerate with build_demo.py"
        )
