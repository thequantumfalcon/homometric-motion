"""Bounded malformed-artifact controls for the optional numerical-study task."""

import hashlib
import io
import json
import runpy
import shutil
import tarfile
from collections.abc import Callable
from pathlib import Path


def check_controls(destination: Path) -> dict:
    """Check rejection paths using synthetic source bytes, without running the study."""
    helper = runpy.run_path(str(Path(__file__).with_name("verify_finite_motion.py")))
    verified_files = helper["verified_files"]
    extract_reviewed = helper["extract_reviewed"]
    destination.mkdir(parents=True, exist_ok=False)
    source = destination / "valid-source"
    source.mkdir()
    entries = []
    for name in sorted(helper["SOURCE_FILES"]):
        data = f"synthetic artifact control: {name}\n".encode()
        (source / name).write_bytes(data)
        entries.append({"path": name, "sha256": hashlib.sha256(data).hexdigest()})
    manifest = {"schema": 1, "kind": "numerical-study-source", "files": entries}
    (source / helper["MANIFEST"]).write_text(json.dumps(manifest), encoding="utf-8")
    files = verified_files(source)
    prefix = "synthetic-package/studies/finite-motion/"

    def archive(name: str, members: dict[str, bytes]) -> Path:
        path = destination / f"{name}.tar.gz"
        with tarfile.open(path, "w:gz") as stream:
            for member_name, data in members.items():
                member = tarfile.TarInfo(member_name)
                member.size = len(data)
                stream.addfile(member, io.BytesIO(data))
        return path

    def rejected(action: Callable[[], object], reason: str) -> None:
        try:
            action()
        except RuntimeError as error:
            if reason not in str(error):
                raise RuntimeError(
                    f"artifact control failed for an unexpected reason: {error}"
                ) from error
        else:
            raise RuntimeError(f"artifact control accepted invalid input: {reason}")

    members = {prefix + name: data for name, data in files.items()}
    valid_destination = destination / "valid-extracted"
    extract_reviewed(archive("valid", members), files, valid_destination)
    if {path.name: path.read_bytes() for path in valid_destination.iterdir()} != files:
        raise RuntimeError("valid artifact control did not preserve reviewed bytes")

    changed = destination / "changed-reference"
    shutil.copytree(source, changed)
    (changed / "results.json").write_bytes(b"changed numerical reference\n")
    rejected(lambda: verified_files(changed), "source manifest mismatch")

    malicious = destination / "malicious-manifest"
    shutil.copytree(source, malicious)
    altered = json.loads(json.dumps(manifest))
    altered["files"][0]["path"] = "../escaped.json"
    (malicious / helper["MANIFEST"]).write_text(json.dumps(altered), encoding="utf-8")
    rejected(lambda: verified_files(malicious), "invalid file inventory")

    incomplete = dict(members)
    del incomplete[prefix + "results.json"]
    incomplete_archive = archive("incomplete", incomplete)
    rejected(
        lambda: extract_reviewed(incomplete_archive, files, destination / "incomplete-extracted"),
        "archive is incomplete",
    )

    traversal = dict(members)
    traversal[prefix + "../../../escaped.json"] = b"untrusted traversal\n"
    traversal_archive = archive("traversal", traversal)
    rejected(
        lambda: extract_reviewed(traversal_archive, files, destination / "traversal-extracted"),
        "invalid finite-motion archive path",
    )

    extra = dict(members)
    extra[prefix + "unexpected.txt"] = b"unreviewed source\n"
    extra_archive = archive("extra", extra)
    rejected(
        lambda: extract_reviewed(extra_archive, files, destination / "extra-extracted"),
        "unexpected or duplicate",
    )
    return {
        "status": "PASS",
        "valid_extraction": True,
        "rejected_cases": [
            "changed_reference_digest",
            "malicious_manifest_path",
            "incomplete_archive",
            "archive_path_traversal",
            "unexpected_archive_member",
        ],
    }
