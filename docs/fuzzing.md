# Arithmetic and rational-input fuzzing

The optional Atheris campaign exercises the installed package's saved-rational
parser and outward interval primitives. These functions underpin saved-result
inspection and exact numerical certificates. Fuzzing seeks implementation bugs;
it does not prove the mathematical construction or validate an experiment.

On Linux x86_64 with Python 3.12, create and activate a development environment,
then run:

```sh
python tools/project.py setup
python tools/project.py fuzz
```

The command builds and verifies the wheel, installs it in a fresh environment,
and installs the single hash-locked Atheris wheel from `requirements-fuzz.txt`.
It copies the development harness beside that environment and invokes Python
in isolated mode. Neither the package import nor its calculations use `src`.
The certificate runtime and the ordinary installed-wheel tests require no
Atheris dependency. The separate Linux CI job runs the same command and is
included in the required `ci` result.

Each campaign starts from explicit seeds covering valid and malformed rationals,
Unicode and invalid UTF-8, signed and zero-crossing intervals, values below the
10^-72 arithmetic grid, and integers adjacent to perfect powers. Atheris mutates
these inputs using coverage feedback. The oracles check:

- Accepted rational text against an independent ASCII grammar and Python's
  `Fraction` parser, including canonical serialization and round trips.
- Interval addition, subtraction, multiplication and division against exact
  rational endpoint extrema, including rejection of zero-containing divisors.
- Integer powers including the interior zero minimum of even powers, and roots
  through exact power inequalities and adjacent-integer brackets.

The harness caps each input at 2,048 bytes, arithmetic operands at fixed byte
widths and powers/root degrees at six. The campaign runs for about 60 seconds,
with a five-second per-input timeout and a 1 GiB fuzzer memory limit. This bounded
campaign does not exhaust the parser's 100,000-character input domain. Dedicated
unit tests retain the large-number and length-boundary checks.

Binary seeds, newly discovered inputs and failure artifacts remain under the
ignored `.build/artifact-*/` directory. A failure's printed command can replay
the saved input with the copied harness and installed environment. Preserve the
smallest failing input and add a deterministic regression test when fixing a
bug. Do not weaken an oracle merely to finish a campaign.

On CI failure, a seven-day `fuzz-failure-inputs` artifact retains only matching
crash, timeout, out-of-memory or leak inputs, when the fuzzer produced them.
The environment and unrelated build files are excluded. Replaying an existing
input file or continuing an existing corpus preserves its bytes.

`tests/test_fuzz_invariants.py` executes every seed without Atheris and deliberately
injects parser, rounding and root errors to ensure that the oracles detect them.
The ordinary unit suite checks these controls on Windows and Linux. CI executes
the actual Atheris engine only on the supported Linux/Python combination.

Atheris 3.1.0's CPython 3.12 manylinux x86_64 wheel is obtained from
[PyPI](https://pypi.org/project/atheris/3.1.0/); it includes libFuzzer and declares
no Python dependencies. Its SHA-256 is pinned in the separate fuzzing lock.
See the [Atheris documentation](https://github.com/google/atheris) for coverage
instrumentation and replay flags. This is a local/CI fuzzing integration, with
no enrollment in an external continuous-fuzzing service.
