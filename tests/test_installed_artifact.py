"""Exercise resources and the CLI from the installed distribution."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from importlib import metadata, resources
from pathlib import Path
from unittest import mock

from test_certificate import certificate

import homometric_motion
from homometric_motion.cli import MANIFEST_FILES, verify_source_manifest


class InstalledArtifactTests(unittest.TestCase):
    def test_import_is_from_installed_distribution(self):
        repository_source = Path(__file__).resolve().parents[1] / "src"
        package_path = Path(homometric_motion.__file__).resolve()
        self.assertFalse(package_path.is_relative_to(repository_source))
        self.assertEqual(metadata.version("homometric-motion"), homometric_motion.__version__)

    def test_manifest_rejects_mutation_and_path_substitution(self):
        source = resources.files("homometric_motion")
        with tempfile.TemporaryDirectory() as temporary:
            copy = Path(temporary)
            for name in MANIFEST_FILES | {"source_manifest.json"}:
                (copy / name).write_bytes(source.joinpath(name).read_bytes())
            with mock.patch("homometric_motion.cli.files", return_value=copy):
                self.assertEqual(len(verify_source_manifest()["bindings"]), len(MANIFEST_FILES))
                protocol = copy / "protocol.json"
                original = protocol.read_bytes()
                protocol.write_bytes(original + b"\n")
                with self.assertRaisesRegex(ValueError, "digest mismatch"):
                    verify_source_manifest()
                protocol.write_bytes(original)
                manifest_file = copy / "source_manifest.json"
                manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
                manifest["files"][0]["path"] = "../inputs.json"
                manifest_file.write_text(json.dumps(manifest), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "allowlist"):
                    verify_source_manifest()

    def test_cli_reproduces_api_and_refuses_to_overwrite(self):
        executable = os.environ.get("HM_TEST_PYTHON", sys.executable)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            output = directory / "certificate.json"
            command = [
                executable,
                "-I",
                "-B",
                "-m",
                "homometric_motion",
                "verify",
                "--output",
                str(output),
            ]
            process = subprocess.run(
                command, cwd=directory, capture_output=True, text=True, timeout=120, check=False
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(process.stderr, "")
            self.assertIn("975,281,623,024,726,766,278", process.stdout)
            self.assertIn("under the declared model", process.stdout)
            encoded = output.read_bytes()
            result = json.loads(encoded)
            provenance = result.pop("source_revision")
            self.assertEqual(provenance, verify_source_manifest())
            self.assertEqual(result, certificate())
            # The output has no execution-time or machine-path fields, so it can
            # be compared as an exact deterministic mathematical record.
            self.assertEqual(set(directory.iterdir()), {output})
            again = subprocess.run(
                command, cwd=directory, capture_output=True, text=True, timeout=120, check=False
            )
            self.assertNotEqual(again.returncode, 0)
            self.assertIn("output exists", again.stderr)
            self.assertEqual(output.read_bytes(), encoded)
            show = subprocess.run(
                [executable, "-I", "-B", "-m", "homometric_motion", "summary", str(output)],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(show.returncode, 0, show.stderr)
            self.assertIn("UNVERIFIED DISPLAY", show.stdout)
            self.assertNotEqual(show.stdout, process.stdout)
            self.assertIn("975,281,623,024,726,766,278", show.stdout)
            for key in ("count", "frequency"):
                modified = json.loads(encoded)
                if key == "count":
                    modified["stages"]["counts"]["sufficient_observation_windows"] = 1
                else:
                    modified["parameters"]["frequency_error_cap_exact"] = "1"
                altered = directory / f"altered-{key}.json"
                altered.write_text(json.dumps(modified), encoding="utf-8")
                rejected = subprocess.run(
                    [executable, "-I", "-B", "-m", "homometric_motion", "summary", str(altered)],
                    cwd=directory,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
                self.assertNotEqual(rejected.returncode, 0)


if __name__ == "__main__":
    unittest.main()
