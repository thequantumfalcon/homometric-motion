"""Install the reviewed Lean release under .build without changing the host.

Release digests and sizes: https://github.com/leanprover/lean4/releases/tag/v4.35.0
The official ZIPs use `zip -rq` and contain regular files, including dereferenced
links. Restore their executable bits on Linux; reject archive links explicitly.
"""

import hashlib
import json
import os
import platform
import re
import stat
import subprocess
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

VERSION = "4.35.0"
RELEASE = f"https://github.com/leanprover/lean4/releases/download/v{VERSION}"
ARCHIVES = {
    "windows": {
        "sha256": "5fc033e93e1a7bc59c5ebf311103d2c9cd18d4b3eddda4ffa3414e8adb0ef79e",
        "size": 902262322,
    },
    "linux": {
        "sha256": "c8531faaa4a93d5a4dae0c742cbc1bd42a2993594d02f93a9d629ebf299fb2c8",
        "size": 925899528,
    },
}
RECEIPT = ".toolchain-install.json"
CHUNK = 1024 * 1024


def _native_platform() -> str:
    system = platform.system().lower()
    if system not in ARCHIVES or platform.machine().lower() not in {"amd64", "x86_64"}:
        raise RuntimeError("automatic Lean setup supports only native x64 Windows and Linux")
    return system


def _no_link(path: Path) -> None:
    """Reject symbolic links and Windows junctions, including dangling links."""
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & getattr(
        stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0
    ):
        raise RuntimeError(f"Lean setup refuses linked paths: {path}")


def _paths(root: Path, system: str, *, create: bool) -> tuple[Path, Path]:
    root = root.resolve(strict=True)
    build = root / ".build"
    downloads = build / "lean-downloads"
    toolchains = build / "toolchains"
    for directory in (build, downloads, toolchains):
        _no_link(directory)
        if create:
            directory.mkdir(exist_ok=True)
        if not directory.is_dir():
            raise RuntimeError("Lean is not set up; run python tools/project.py lean-setup")
    name = f"lean-{VERSION}-{system}"
    archive, installed = downloads / f"{name}.zip", toolchains / name
    _no_link(archive)
    _no_link(installed)
    return archive, installed


def _verify_archive(archive: Path, expected: dict) -> None:
    _no_link(archive)
    if not archive.is_file() or archive.stat().st_size != expected["size"]:
        raise RuntimeError(f"Lean archive is missing or has the wrong size: {archive}")
    with archive.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    if digest != expected["sha256"]:
        raise RuntimeError(f"Lean archive SHA-256 does not match the reviewed release: {archive}")


def _download(archive: Path, expected: dict) -> None:
    partial = archive.with_suffix(".zip.part")
    _no_link(partial)
    request = urllib.request.Request(
        f"{RELEASE}/{archive.name}", headers={"User-Agent": "homometric-motion-lean-setup"}
    )
    count = 0
    started = time.monotonic()
    # Exclusive creation preserves any previous incomplete download for inspection.
    with partial.open("xb") as target, urllib.request.urlopen(request, timeout=60) as source:
        while chunk := source.read(CHUNK):
            count += len(chunk)
            if count > expected["size"] or time.monotonic() - started > 1800:
                raise RuntimeError("Lean download exceeded its declared size or 30-minute limit")
            target.write(chunk)
    _verify_archive(partial, expected)
    if archive.exists():
        raise RuntimeError(
            f"Lean archive appeared during download; refusing replacement: {archive}"
        )
    partial.rename(archive)


def _members(archive: zipfile.ZipFile, prefix: str) -> dict[str, zipfile.ZipInfo]:
    members = {}
    folded = set()
    total = 0
    for entry in archive.infolist():
        name = entry.filename.removesuffix("/")
        parts = name.split("/")
        if (
            not parts
            or parts[0] != prefix
            or any(part in {"", ".", ".."} for part in parts)
            or any(character in name for character in "\\:\x00")
            or any(ord(character) < 32 for character in name)
        ):
            raise RuntimeError(f"unsafe Lean archive path: {entry.filename!r}")
        relative = "/".join(parts[1:])
        mode = entry.external_attr >> 16
        kind = stat.S_IFMT(mode)
        if kind not in {0, stat.S_IFREG, stat.S_IFDIR} or (
            kind == stat.S_IFDIR and not entry.is_dir()
        ):
            raise RuntimeError("Lean archive contains a link or unsupported entry type")
        if not relative:
            if not entry.is_dir():
                raise RuntimeError("Lean archive root must be a directory")
            continue
        if relative.casefold() in folded or relative == RECEIPT:
            raise RuntimeError("Lean archive has duplicate or reserved paths")
        folded.add(relative.casefold())
        members[relative] = entry
        total += entry.file_size
        if total > 12_000_000_000 or len(members) > 150_000:
            raise RuntimeError("Lean archive exceeds the extraction bounds")
    if not members:
        raise RuntimeError("Lean archive is empty")
    for relative in members:
        for parent in Path(relative).parents:
            if parent.as_posix() in members and not members[parent.as_posix()].is_dir():
                raise RuntimeError("Lean archive places a file above another member")
    return members


def _extract(archive: Path, destination: Path, prefix: str) -> None:
    # The caller checks the pinned archive digest before this function is entered.
    destination.mkdir(exist_ok=False)
    with zipfile.ZipFile(archive) as source:
        members = _members(source, prefix)
        for relative, entry in members.items():
            output = destination / relative
            if entry.is_dir():
                output.mkdir(parents=True, exist_ok=True)
                continue
            output.parent.mkdir(parents=True, exist_ok=True)
            with source.open(entry) as incoming, output.open("xb") as target:
                while chunk := incoming.read(CHUNK):
                    target.write(chunk)
            if os.name != "nt":
                output.chmod(0o755 if entry.external_attr >> 16 & 0o111 else 0o644)


def _receipt(system: str) -> dict:
    return {
        "schema": 1,
        "version": VERSION,
        "platform": system,
        "archive": f"lean-{VERSION}-{system}.zip",
        **ARCHIVES[system],
    }


def _verify_tree(archive: Path, installed: Path, system: str) -> None:
    _no_link(installed)
    if not installed.is_dir():
        raise RuntimeError("Lean is not set up; run python tools/project.py lean-setup")
    receipt = installed / RECEIPT
    _no_link(receipt)
    if not receipt.is_file() or json.loads(receipt.read_text("utf-8")) != _receipt(system):
        raise RuntimeError("existing Lean directory lacks the matching setup receipt")
    with zipfile.ZipFile(archive) as source:
        members = _members(source, installed.name)
        expected = {name for name, entry in members.items() if not entry.is_dir()}
        actual = set()
        for directory, names, filenames in os.walk(installed, followlinks=False):
            for name in [*names, *filenames]:
                _no_link(Path(directory) / name)
            for name in filenames:
                path = Path(directory) / name
                if not path.is_file():
                    raise RuntimeError("existing Lean directory contains a special file")
                actual.add(path.relative_to(installed).as_posix())
        if actual != expected | {RECEIPT}:
            raise RuntimeError("existing Lean directory has missing or extra files")
        # Compare to the authenticated archive, not hashes in a mutable local receipt.
        for relative in sorted(expected):
            entry = members[relative]
            path = installed / relative
            if path.stat().st_size != entry.file_size:
                raise RuntimeError(f"installed Lean file differs from release: {relative}")
            with source.open(entry) as original, path.open("rb") as current:
                while chunk := original.read(CHUNK):
                    if current.read(len(chunk)) != chunk:
                        raise RuntimeError(f"installed Lean file differs from release: {relative}")
            if os.name != "nt" and bool(path.stat().st_mode & 0o111) != bool(
                entry.external_attr >> 16 & 0o111
            ):
                raise RuntimeError(f"installed Lean executable mode differs: {relative}")


def _verify_versions(binary: Path, system: str) -> None:
    suffix = ".exe" if system == "windows" else ""
    environment = dict(os.environ)
    environment["PATH"] = str(binary) + os.pathsep + environment.get("PATH", "")
    for name in ("lean", "lake"):
        result = subprocess.run(
            [str(binary / f"{name}{suffix}"), "--version"],
            cwd=binary,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        if not re.search(rf"\bversion {re.escape(VERSION)}\b", result.stdout):
            raise RuntimeError(f"unexpected {name} version: {result.stdout.strip()}")


def installed_bin(root: Path) -> Path:
    """Validate an existing installation against the pinned archive and return bin."""
    system = _native_platform()
    archive, installed = _paths(root, system, create=False)
    _verify_archive(archive, ARCHIVES[system])
    _verify_tree(archive, installed, system)
    binary = installed / "bin"
    _verify_versions(binary, system)
    return binary


def setup(root: Path) -> Path:
    """Download if absent, verify, and install the official release only under root."""
    system = _native_platform()
    archive, installed = _paths(root, system, create=True)
    if not archive.exists():
        print(f"Downloading the official Lean {VERSION} {system} ZIP...", flush=True)
        _download(archive, ARCHIVES[system])
    _verify_archive(archive, ARCHIVES[system])
    if installed.exists():
        return installed_bin(root)
    staging = Path(tempfile.mkdtemp(prefix=f".{installed.name}-", dir=installed.parent))
    unpacked = staging / installed.name
    print(f"Extracting the verified Lean {VERSION} release...", flush=True)
    _extract(archive, unpacked, installed.name)
    (unpacked / RECEIPT).write_text(
        json.dumps(_receipt(system), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    _verify_versions(unpacked / "bin", system)
    # Both paths are direct children of the validated workspace toolchain directory.
    if not unpacked.resolve().is_relative_to(installed.parent.resolve()) or installed.exists():
        raise RuntimeError("Lean installation destination changed; refusing replacement")
    unpacked.rename(installed)
    staging.rmdir()
    return installed / "bin"


if __name__ == "__main__":
    print(setup(Path(__file__).resolve().parents[1]))
