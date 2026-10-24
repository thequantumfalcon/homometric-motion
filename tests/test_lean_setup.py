"""Offline controls for the optional toolchain installer's integrity boundaries."""

import hashlib
import json
import runpy
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

HELPER = runpy.run_path(str(Path(__file__).resolve().parents[1] / "tools" / "setup_lean.py"))
GLOBALS = HELPER["setup"].__globals__
PREFIX = "lean-4.35.0-windows"


class LeanSetupTests(unittest.TestCase):
    def make_archive(self, root: Path, entries: list[tuple[str, bytes, int]]) -> Path:
        archive = root / "release.zip"
        with zipfile.ZipFile(archive, "w") as output:
            for name, data, mode in entries:
                entry = zipfile.ZipInfo(name)
                entry.external_attr = mode << 16
                output.writestr(entry, data)
        return archive

    def test_digest_failure_precedes_extraction_or_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            download = root / ".build" / "lean-downloads"
            download.mkdir(parents=True)
            archive = download / f"{PREFIX}.zip"
            archive.write_bytes(b"wrong archive")
            expected = {"size": archive.stat().st_size, "sha256": "0" * 64}
            execute = mock.Mock()
            with mock.patch.dict(
                GLOBALS,
                {
                    "_native_platform": lambda: "windows",
                    "ARCHIVES": {"windows": expected},
                    "_verify_versions": execute,
                },
            ):
                with self.assertRaisesRegex(RuntimeError, "SHA-256"):
                    HELPER["setup"](root)
            execute.assert_not_called()
            self.assertFalse((root / ".build" / "toolchains" / PREFIX).exists())

    def test_rejects_archive_traversal_links_and_file_parent(self):
        cases = [
            [(f"{PREFIX}/../escape", b"bad", stat.S_IFREG | 0o644)],
            [(f"{PREFIX}/bin/tool", b"../../outside", stat.S_IFLNK | 0o777)],
            [
                (f"{PREFIX}/bin", b"file", stat.S_IFREG | 0o644),
                (f"{PREFIX}/bin/tool", b"bad", stat.S_IFREG | 0o755),
            ],
            [
                (f"{PREFIX}/bin/Tool", b"a", stat.S_IFREG | 0o755),
                (f"{PREFIX}/bin/tool", b"b", stat.S_IFREG | 0o755),
            ],
        ]
        for entries in cases:
            with self.subTest(entries=entries), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                archive = self.make_archive(root, entries)
                with self.assertRaises(RuntimeError):
                    HELPER["_extract"](archive, root / "out", PREFIX)
                self.assertFalse((root / "escape").exists())

    def test_verified_reuse_and_mutation_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = self.make_archive(
                root,
                [(f"{PREFIX}/bin/lean.exe", b"reviewed binary", stat.S_IFREG | 0o755)],
            )
            expected = {
                "size": archive.stat().st_size,
                "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            }
            installed = root / PREFIX
            HELPER["_extract"](archive, installed, PREFIX)
            receipt = installed / HELPER["RECEIPT"]
            with mock.patch.dict(GLOBALS, {"ARCHIVES": {"windows": expected}}):
                receipt.write_text(json.dumps(HELPER["_receipt"]("windows")), encoding="utf-8")
                HELPER["_verify_archive"](archive, expected)
                HELPER["_verify_tree"](archive, installed, "windows")
                binary = installed / "bin" / "lean.exe"
                binary.write_bytes(b"modified binary")
                with self.assertRaisesRegex(RuntimeError, "differs from release"):
                    HELPER["_verify_tree"](archive, installed, "windows")
                binary.write_bytes(b"reviewed binary")
                extra = installed / "extra.dll"
                extra.write_bytes(b"unexpected")
                with self.assertRaisesRegex(RuntimeError, "missing or extra"):
                    HELPER["_verify_tree"](archive, installed, "windows")
                extra.unlink()
                receipt.write_text("{}", encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, "receipt"):
                    HELPER["_verify_tree"](archive, installed, "windows")

    def test_existing_directory_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            download = root / ".build" / "lean-downloads"
            download.mkdir(parents=True)
            archive = download / f"{PREFIX}.zip"
            archive.write_bytes(b"fixture")
            expected = {
                "size": 7,
                "sha256": hashlib.sha256(b"fixture").hexdigest(),
            }
            installed = root / ".build" / "toolchains" / PREFIX
            installed.mkdir(parents=True)
            marker = installed / "existing.txt"
            marker.write_text("preserve", encoding="utf-8")
            with mock.patch.dict(
                GLOBALS,
                {"_native_platform": lambda: "windows", "ARCHIVES": {"windows": expected}},
            ):
                with self.assertRaisesRegex(RuntimeError, "receipt"):
                    HELPER["setup"](root)
            self.assertEqual(marker.read_text("utf-8"), "preserve")

    def test_setup_and_read_only_reuse_keep_the_same_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.make_archive(
                root,
                [(f"{PREFIX}/bin/lean.exe", b"reviewed binary", stat.S_IFREG | 0o755)],
            )
            download = root / ".build" / "lean-downloads"
            download.mkdir(parents=True)
            archive = download / f"{PREFIX}.zip"
            source.rename(archive)
            expected = {
                "size": archive.stat().st_size,
                "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            }
            execute = mock.Mock()
            fetch = mock.Mock(side_effect=AssertionError("cached setup must not download"))
            with mock.patch.dict(
                GLOBALS,
                {
                    "_native_platform": lambda: "windows",
                    "ARCHIVES": {"windows": expected},
                    "_verify_versions": execute,
                    "_download": fetch,
                },
            ):
                binary = HELPER["setup"](root)
                self.assertEqual(HELPER["installed_bin"](root), binary)
                self.assertEqual(HELPER["setup"](root), binary)
            self.assertEqual((binary / "lean.exe").read_bytes(), b"reviewed binary")
            self.assertEqual(execute.call_count, 3)
            fetch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
