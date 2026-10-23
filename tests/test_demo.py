"""Keep the two display contracts separate and reject misleading exact intervals."""

import importlib.util
import json
import runpy
import tempfile
import unittest
from pathlib import Path

from test_certificate import certificate
from test_profiles import profile_result

from homometric_motion.cli import verify_source_manifest

spec = importlib.util.spec_from_file_location(
    "build_demo", Path(__file__).resolve().parents[1] / "tools" / "build_demo.py"
)
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


def changed(record, path, value):
    """Copy only the ancestors of one changed field; leave shared evidence intact."""
    result = dict(record)
    result[path[0]] = changed(record[path[0]], path[1:], value) if len(path) > 1 else value
    return result


class DemoDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = verify_source_manifest()
        cls.original = dict(certificate(), source_revision=source)
        cls.selected = dict(
            profile_result("long-exposure-v1", "exact_geometry"), source_revision=source
        )
        cls.manifest = source["manifest_sha256"]

    def display(self, selected):
        return demo.profile_display(
            selected, "fixture-certificate-digest", self.original, self.manifest
        )

    def test_selected_display_uses_its_own_shapes_and_threshold(self):
        selected = self.display(self.selected)["certificate"]
        self.assertEqual(selected["sufficient_observation_windows"], "36938105282195")
        self.assertEqual(selected["parameters"]["exposure_cap_exact"], "1/1000")
        self.assertEqual(
            selected["threshold_exact"], self.selected["allocation"]["threshold_exact"]
        )
        self.assertNotEqual(
            selected["threshold_exact"], self.original["stages"]["counts"]["threshold_exact"]
        )
        for side in ("A", "B"):
            self.assertEqual(
                selected["classes"][side]["expanded_skewness_exact"],
                self.selected["allocation"]["expanded_shapes"][side],
            )

    def test_rejects_model_source_and_allocation_mixups(self):
        mutations = [
            (("scenario",), "position_uncertainty"),
            (("profile",), "short-exposure-v1"),
            (("source_revision", "manifest_sha256"), "different-source"),
            (("core_certificate_sha256",), "different-core"),
            (("parameters", "exposure_cap_exact"), "1/100"),
            (("parameters", "frequency_error_cap_exact"), "1/10000000000000000"),
            (("parameters", "h_interval_exact"), ["1", "100"]),
            (("allocation", "sufficient_observation_windows"), 1),
            (("allocation", "individual_class_error_upper", "exact"), "1/10"),
            (("nuisance_evidence", "observation_union", "time_cell_count_per_class"), 511),
            (
                ("allocation", "original_shapes", "A"),
                self.original["stages"]["counts"]["expanded_shape_intervals_exact"]["A"],
            ),
            (
                ("allocation", "classifier", "threshold_exact"),
                self.original["stages"]["counts"]["threshold_exact"],
            ),
        ]
        for path, value in mutations:
            with self.subTest(field=".".join(path)), self.assertRaises(ValueError):
                self.display(changed(self.selected, path, value))

    def test_exact_display_guards_resolve_a_gap_below_float_precision(self):
        # Both critical endpoints round to 1.0; float comparison cannot certify this gap.
        denominator = 10**20
        upper_a = f"{denominator + 1}/{denominator}"
        lower_b = f"{denominator + 3}/{denominator}"
        threshold = f"{denominator + 2}/{denominator}"
        population = {
            "A": {"lower": "1", "upper": upper_a},
            "B": {"lower": lower_b, "upper": "2"},
        }
        expanded = {"A": ["1/2", upper_a], "B": [lower_b, "5/2"]}
        result = demo.shape_classes(population, expanded, threshold, f"2/{denominator}")
        self.assertEqual(result["A"]["skewness_display"][1], result["B"]["skewness_display"][0])
        for threshold_text, gap in ((upper_a, f"2/{denominator}"), (threshold, "0")):
            with self.assertRaises(ValueError):
                demo.shape_classes(population, expanded, threshold_text, gap)

    def test_display_manifest_rejects_asset_mutation_and_missing_manifest(self):
        helper = runpy.run_path(
            str(Path(__file__).resolve().parents[1] / "tools" / "demo_manifest.py")
        )
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for name in helper["ASSETS"]:
                (directory / name).write_text("local display asset\n", encoding="utf-8")
            (directory / "data.json").write_text(
                json.dumps(
                    {
                        "source": {
                            "certificate_sha256": "original-digest",
                            "package_manifest_sha256": "unchanged-package-digest",
                        },
                        "profiles": {
                            "long-exposure-v1": {"source": {"certificate_sha256": "profile-digest"}}
                        },
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(RuntimeError):
                helper["check_manifest"](directory)
            manifest = helper["build_manifest"](directory)
            (directory / "SOURCE_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
            helper["check_manifest"](directory)
            (directory / "app.js").write_text("changed display behavior\n", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                helper["check_manifest"](directory)


if __name__ == "__main__":
    unittest.main()
