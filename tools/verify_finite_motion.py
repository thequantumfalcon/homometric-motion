"""Replay the optional numerical study from the reviewed source archive.

This verifier uses the standard library. Executing the separately packaged
study requires its hash-locked mpmath dependency in the active environment.
The resulting receipt concerns numerical reproduction, not a risk certificate.
"""

import argparse
import hashlib
import json
import runpy
import subprocess
import sys
import tarfile
from pathlib import Path, PurePosixPath

SOURCE_FILES = frozenset(
    {"README.md", "finite_motion.py", "requirements.txt", "results.json", "mixed-results.json"}
)
MANIFEST = "source_manifest.json"


def verified_files(source: Path) -> dict[str, bytes]:
    """Read only the fixed inventory after checking its separate SHA-256 manifest."""
    if (source / MANIFEST).is_symlink():
        raise RuntimeError("finite-motion manifest must not be a symbolic link")
    manifest_bytes = (source / MANIFEST).read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") != 1 or manifest.get("kind") != "numerical-study-source":
        raise RuntimeError("unsupported finite-motion source manifest")
    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise RuntimeError("finite-motion manifest must list its files")
    paths = [entry.get("path") for entry in entries]
    if len(paths) != len(SOURCE_FILES) or set(paths) != SOURCE_FILES:
        raise RuntimeError("finite-motion manifest has an invalid file inventory")
    inventory = {path.name for path in source.iterdir() if path.is_file()}
    if inventory != SOURCE_FILES | {MANIFEST}:
        raise RuntimeError("finite-motion source contains missing or unexpected files")
    files = {MANIFEST: manifest_bytes}
    for entry in entries:
        name = entry["path"]
        path = source / name
        if path.is_symlink():
            raise RuntimeError("finite-motion source files must not be symbolic links")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != entry.get("sha256"):
            raise RuntimeError(f"finite-motion source manifest mismatch: {name}")
        files[name] = data
    return files


def extract_reviewed(archive: Path, files: dict[str, bytes], destination: Path) -> None:
    """Copy only matching regular study files; never use tarfile.extract/extractall."""
    destination.mkdir(parents=True, exist_ok=False)
    seen = set()
    roots = set()
    with tarfile.open(archive, "r:gz") as source:
        for member in source:
            parts = PurePosixPath(member.name).parts
            if len(parts) < 3 or parts[1:3] != ("studies", "finite-motion"):
                continue
            if "\\" in member.name or ".." in parts or PurePosixPath(member.name).is_absolute():
                raise RuntimeError("invalid finite-motion archive path")
            if member.isdir():
                continue
            if len(parts) != 4 or not member.isfile():
                raise RuntimeError("invalid finite-motion archive member")
            name = parts[-1]
            if name not in files or name in seen:
                raise RuntimeError("unexpected or duplicate finite-motion archive file")
            if member.size != len(files[name]):
                raise RuntimeError("finite-motion archive size differs from reviewed source")
            stream = source.extractfile(member)
            if stream is None or stream.read() != files[name]:
                raise RuntimeError("finite-motion archive differs from reviewed source")
            (destination / name).write_bytes(files[name])
            roots.add(parts[0])
            seen.add(name)
    if seen != set(files) or len(roots) != 1:
        raise RuntimeError("finite-motion source archive is incomplete or has multiple roots")


def run_study(script: Path, output: Path, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-I", str(script), "verify", "--output", str(output)],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=600,
        check=False,
    )


def verify_archive(archive: Path, reviewed_source: Path, destination: Path) -> dict:
    files = verified_files(reviewed_source.resolve())
    archive = archive.resolve()
    destination = destination.resolve()
    dependency = subprocess.run(
        [sys.executable, "-I", "-c", "import mpmath; print(mpmath.__version__)"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if dependency.returncode or dependency.stdout.strip() != "1.4.1":
        raise RuntimeError("install the finite-motion hash-locked requirements before this task")
    destination.mkdir(parents=True, exist_ok=False)
    controls = runpy.run_path(Path(__file__).with_name("check_finite_motion_controls.py"))[
        "check_controls"
    ](destination / "controls")
    source = destination / "source"
    extract_reviewed(archive, files, source)
    script = source / "finite_motion.py"
    receipts = []
    logs = []
    for number in (1, 2):
        run_dir = destination / f"run-{number}"
        run_dir.mkdir()
        output = run_dir / "verification.json"
        result = run_study(script, output, run_dir)
        (run_dir / "stdout.txt").write_text(result.stdout, encoding="utf-8", newline="\n")
        (run_dir / "stderr.txt").write_text(result.stderr, encoding="utf-8", newline="\n")
        if result.returncode:
            raise RuntimeError(f"packaged finite-motion numerical replay failed: {result.stderr}")
        receipts.append(output.read_bytes())
        logs.append(result.stdout)
        refusal = run_study(script, output, run_dir)
        if (
            refusal.returncode == 0
            or "refusing to overwrite" not in refusal.stderr
            or output.read_bytes() != receipts[-1]
        ):
            raise RuntimeError("finite-motion overwrite refusal failed")
    if receipts[0] != receipts[1] or logs[0] != logs[1]:
        raise RuntimeError("finite-motion numerical replays are not deterministic")
    record = json.loads(receipts[0])
    if (
        record.get("status") != "PASS"
        or record.get("sweep_rows") != 10
        or record.get("mixed_rows") != 12
        or record.get("precision_digits") != 110
    ):
        raise RuntimeError("finite-motion numerical replay receipt is incomplete")
    for name, data in files.items():
        if (source / name).read_bytes() != data:
            raise RuntimeError("finite-motion replay modified the packaged source")
    prohibited = run_study(script, source / "fresh-output.json", destination)
    if prohibited.returncode == 0 or "outside the study source directory" not in prohibited.stderr:
        raise RuntimeError("finite-motion source-output isolation failed")
    receipt = {
        "status": "PASS",
        "kind": "optional numerical study reproduction; not a risk certificate",
        "source_archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "source_manifest_sha256": hashlib.sha256(files[MANIFEST]).hexdigest(),
        "repeated_output_sha256": hashlib.sha256(receipts[0]).hexdigest(),
        "dependency": "mpmath==1.4.1",
        "repeated_runs": 2,
        "overwrite_refusal": True,
        "source_output_isolation": True,
        "artifact_controls": controls,
        "numerical_checks": record,
    }
    (destination / "verification.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify_archive(args.archive, args.source, args.destination), indent=2))


if __name__ == "__main__":
    main()
