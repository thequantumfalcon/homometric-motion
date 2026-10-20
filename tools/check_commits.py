"""Check DCO sign-off and commit-message policy for reachable history."""

import re
import subprocess


def main() -> None:
    commits = subprocess.check_output(
        ["git", "log", "--format=%H%x00%an%x00%ae%x00%B%x00"], text=True, encoding="utf-8"
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
