"""Verify the files named by this kit's manifest; no network or external paths."""

import json
from hashlib import sha256
from pathlib import Path, PurePosixPath

root = Path(__file__).resolve().parent
manifest = json.loads((root / "SOURCE_MANIFEST.json").read_text("utf-8"))
for name, item in manifest["files"].items():
    relative = PurePosixPath(name)
    if relative.is_absolute() or ".." in relative.parts or ":" in name or "\\" in name:
        raise ValueError("Invalid manifest path")
    path = root.joinpath(*relative.parts)
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise ValueError("Manifest path leaves the kit")
    raw = path.read_bytes()
    if len(raw) != item["bytes"] or sha256(raw).hexdigest() != item["sha256"]:
        raise ValueError("Manifest mismatch: " + name)
print(
    "PASS: "
    + str(len(manifest["files"]))
    + " manifest entries; this is an integrity check, not a signature"
)
