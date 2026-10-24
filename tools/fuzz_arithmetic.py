"""Coverage-guided Atheris entry point, copied beside its helper before execution."""

import sys
from pathlib import Path

import atheris

# project.py copies these two development files into a fresh artifact directory.
# The scientific package is imported from the installed wheel, never from src.
sys.path.insert(0, str(Path(__file__).resolve().parent))
with atheris.instrument_imports():
    from fuzz_invariants import check_input, prepare_corpus


@atheris.instrument_func
def test_one_input(data):
    check_input(data)


def main():
    corpus = Path(sys.argv[1])
    prepare_corpus(corpus)
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
