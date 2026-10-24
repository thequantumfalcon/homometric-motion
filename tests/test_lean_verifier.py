"""Negative controls for formal-artifact integrity and proof-report acceptance."""

import io
import json
import runpy
import shutil
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HELPER = runpy.run_path(str(ROOT / "tools/verify_lean.py"))


class LeanReportTests(unittest.TestCase):
    def setUp(self):
        self.finite_names = (
            "selected_position_shape_gap",
            "expanded_count_rule_gap",
            "ceiling_lower",
            "ceiling_upper",
            "recorded_individual_error_at_most_one_twentieth",
            "positive_position_contact_margin",
        )
        self.output = "\n".join(
            f"'CertificateCheckpoint.{name}' does not depend on any axioms"
            for name in self.finite_names
        )

    def test_complete_finite_reports_and_empty_module_are_accepted(self):
        result = HELPER["check_axioms"]("CertificateCheckpoint", self.output)
        self.assertEqual(len(result), 6)
        self.assertTrue(all(not axioms for axioms in result.values()))
        self.assertEqual(HELPER["check_axioms"]("GraphCommon", "\n"), {})

    def test_multiline_foundations_are_accepted(self):
        output = "\n".join(
            f"'FactorialCheckpoint.product{name}' depends on axioms:\n"
            "[propext,\n Classical.choice, Quot.sound]"
            for name in ("11", "12", "13", "22", "23", "33")
        )
        self.assertEqual(len(HELPER["check_axioms"]("FactorialIdentities", output)), 6)

    def test_missing_duplicate_wrong_name_and_reordered_reports_are_rejected(self):
        lines = self.output.splitlines()
        cases = (
            "\n".join(lines[:-1]),
            self.output + "\n" + lines[0],
            self.output.replace("CertificateCheckpoint.ceiling_lower", "Other.ceiling_lower"),
            "\n".join(reversed(lines)),
        )
        for output in cases:
            with self.subTest(output=output), self.assertRaises(RuntimeError):
                HELPER["check_axioms"]("CertificateCheckpoint", output)

    def test_axioms_sorry_and_diagnostics_are_rejected(self):
        for axioms in ("sorryAx", "native_decide", "MyAxiom", "propext"):
            output = self.output.replace(
                "does not depend on any axioms", f"depends on axioms: [{axioms}]", 1
            )
            with (
                self.subTest(axioms=axioms),
                self.assertRaisesRegex(RuntimeError, "unexpected axioms"),
            ):
                HELPER["check_axioms"]("CertificateCheckpoint", output)
        for extra in ("warning: declaration uses sorry", "unrecognized report", "[]"):
            with self.subTest(extra=extra), self.assertRaises(RuntimeError):
                HELPER["check_axioms"]("CertificateCheckpoint", extra + "\n" + self.output)
        with self.assertRaisesRegex(RuntimeError, "stderr"):
            HELPER["check_axioms"]("CertificateCheckpoint", self.output, "warning")

    def test_source_proof_escapes_are_rejected_but_comments_are_ignored(self):
        check = HELPER["check_lean_source"]
        check("GraphCommon", b"/- sorry /- axiom -/ native_decide -/\n-- admit\n")
        for code in (
            b"theorem bad : False := by sorry\n",
            b"theorem bad : False := by admit\n",
            b"axiom hidden : False\n",
            b"theorem bad : True := by native_decide\n",
            b"set_option debug.skipKernelTC true\n",
        ):
            with self.subTest(code=code), self.assertRaisesRegex(RuntimeError, "proof escape"):
                check("GraphCommon", code)
        with self.assertRaisesRegex(RuntimeError, "unterminated"):
            check("GraphCommon", b"/- unfinished comment")
        with self.assertRaisesRegex(RuntimeError, "statement inventory"):
            check("GraphCommon", b"#print axioms Unexpected.theorem\n")

    def test_type_displays_are_rejected_at_preflight_without_relaxing_output_checks(self):
        for directive in (b"#check @Nat.add\n", b"#eval 1 + 1\n", b"#print Nat.add\n"):
            with (
                self.subTest(directive=directive),
                self.assertRaisesRegex(RuntimeError, "diagnostic directive"),
            ):
                HELPER["check_lean_source"]("GraphCommon", directive)
        with self.assertRaisesRegex(RuntimeError, "axiom reports"):
            HELPER["check_axioms"](
                "CertificateCheckpoint", self.output + "\n@ceiling_lower : 0 < 1\n"
            )


class LeanArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.files = {"a.lean": b"import Init\n", "analytic/b.lean": b"import Std\n"}
        self.prefix = "package/docs/proofs/formal/"

    def archive(self, entries):
        path = self.directory / "source.tar.gz"
        with tarfile.open(path, "w:gz") as archive:
            for name, data, kind in entries:
                member = tarfile.TarInfo(name)
                member.type = kind
                member.size = len(data) if kind == tarfile.REGTYPE else 0
                if kind == tarfile.SYMTYPE:
                    member.linkname = "../../outside"
                archive.addfile(member, io.BytesIO(data) if member.isfile() else None)
        return path

    def entries(self):
        return [(self.prefix + name, raw, tarfile.REGTYPE) for name, raw in self.files.items()]

    def test_reviewed_archive_extracts_exact_bytes_and_refuses_existing_destination(self):
        destination = self.directory / "out"
        archive = self.archive(self.entries())
        HELPER["extract_reviewed"](archive, self.files, destination)
        for name, raw in self.files.items():
            self.assertEqual((destination / name).read_bytes(), raw)
        with self.assertRaises(FileExistsError):
            HELPER["extract_reviewed"](archive, self.files, destination)

    def test_malformed_archives_are_rejected(self):
        entries = self.entries()
        cases = {
            "missing": entries[:-1],
            "duplicate": entries + [entries[0]],
            "extra": entries + [(self.prefix + "extra.lean", b"unreviewed", tarfile.REGTYPE)],
            "traversal": entries + [(self.prefix + "../escape", b"bad", tarfile.REGTYPE)],
            "backslash": entries + [(self.prefix + "a\\b", b"bad", tarfile.REGTYPE)],
            "symlink": [(entries[0][0], b"", tarfile.SYMTYPE)] + entries[1:],
            "different_bytes": [(entries[0][0], b"import Fake\n", tarfile.REGTYPE)] + entries[1:],
            "second_root": entries + [("other/unrelated.txt", b"bad", tarfile.REGTYPE)],
        }
        for name, malformed in cases.items():
            with self.subTest(name=name), self.assertRaises(RuntimeError):
                HELPER["extract_reviewed"](
                    self.archive(malformed), self.files, self.directory / name
                )

    def test_analytic_manifest_rejects_changed_source_and_path_substitution(self):
        source = self.directory / "reviewed" / HELPER["FORMAL"]
        shutil.copytree(
            ROOT / HELPER["FORMAL"], source, ignore=shutil.ignore_patterns(".lake", "__pycache__")
        )
        reviewed = self.directory / "reviewed"
        HELPER["verified_files"](reviewed)
        path = source / "analytic/SCOPE.md"
        original = path.read_bytes()
        path.write_bytes(original + b"changed\n")
        with self.assertRaisesRegex(RuntimeError, "manifest mismatch"):
            HELPER["verified_files"](reviewed)
        path.write_bytes(original)
        manifest_path = source / "analytic/source_manifest.json"
        manifest = json.loads(manifest_path.read_text("utf-8"))
        manifest["files"][0]["path"] = "../escape"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "manifest inventory"):
            HELPER["verified_files"](reviewed)

    def test_changed_source_is_rejected_after_execution(self):
        source = self.directory / "source"
        source.mkdir()
        (source / "a.lean").write_bytes(b"changed")
        with self.assertRaisesRegex(RuntimeError, "modified packaged source"):
            HELPER["check_sources"](source, {"a.lean": self.files["a.lean"]})

    def test_wheel_import_hook_is_rejected_before_installation(self):
        package = self.directory / "package"
        package.mkdir()
        (package / "__init__.py").write_bytes(b"# reviewed\n")
        wheel = self.directory / "untrusted.whl"
        with zipfile.ZipFile(wheel, "w") as archive:
            archive.writestr("homometric_motion/__init__.py", b"# reviewed\n")
            for name in (
                "licenses/LICENSE.txt",
                "METADATA",
                "WHEEL",
                "entry_points.txt",
                "top_level.txt",
                "RECORD",
            ):
                archive.writestr("homometric_motion-0.1.0.dist-info/" + name, b"metadata")
        HELPER["check_wheel"](wheel, package)
        with zipfile.ZipFile(wheel, "a") as archive:
            archive.writestr("unreviewed.pth", b"import unreviewed\n")
        with self.assertRaisesRegex(RuntimeError, "unexpected wheel payload"):
            HELPER["check_wheel"](wheel, package)


if __name__ == "__main__":
    unittest.main()
