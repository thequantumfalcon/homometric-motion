"""Check DCO sign-off and commit-message policy for reachable history."""

import os
import re
import subprocess


def main() -> None:
    # PR workflows check out a synthetic merge commit without contributor sign-off.
    # Check the submitted head instead; never treat that generated merge as an
    # inbound contribution or interpolate an untrusted revision into a shell.
    ref = os.environ.get("COMMIT_POLICY_REF", "HEAD")
    if ref != "HEAD" and not re.fullmatch(r"[0-9a-f]{40}", ref):
        raise SystemExit("COMMIT_POLICY_REF must be a full commit SHA")
    commits = subprocess.check_output(
        ["git", "log", "--format=%H%x00%an%x00%ae%x00%B%x00", ref, "--"],
        text=True,
        encoding="utf-8",
    ).split("\0")
    checked = 0
    for offset in range(0, len(commits) - 3, 4):
        commit, author, email, body = commits[offset : offset + 4]
        expected = f"Signed-off-by: {author} <{email}>"
        if expected not in body.splitlines():
            raise SystemExit(f"{commit.strip()}: missing author-matching DCO sign-off")
        if re.search(r"(?im)^co-authored-by:", body):
            raise SystemExit(f"{commit.strip()}: coauthor trailers are outside project policy")
        checked += 1
    if checked == 0:
        raise SystemExit("No commits were available to verify")
    print(f"PASS: DCO and message policy for {checked} reachable commits")


if __name__ == "__main__":
    main()
