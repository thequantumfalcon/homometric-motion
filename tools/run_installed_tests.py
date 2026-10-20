"""Run repository tests against an explicitly installed wheel, never src."""

import importlib
import sys
import unittest
from pathlib import Path


def main() -> int:
    site, tests = (Path(value).resolve() for value in sys.argv[1:])
    sys.path.insert(0, str(site))
    package = importlib.import_module("homometric_motion")
    if not Path(package.__file__).resolve().is_relative_to(site):
        raise RuntimeError("tests imported a package outside the installed artifact")
    suite = unittest.defaultTestLoader.discover(str(tests))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
