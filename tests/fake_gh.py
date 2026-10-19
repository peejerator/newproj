"""A stand-in for the GitHub CLI, put on PATH by the tests. It never touches the network.

FAKE_GH_MODE selects the behavior: `ok` (default), `unauthenticated`, `no-user`, or
`fail-create`. `repo create` makes a local bare repository under FAKE_GH_REMOTES and
pushes to it. Every call is appended to FAKE_GH_LOG, one line per call.
"""

import os
import subprocess
import sys
from pathlib import Path

USER = "fake-user"


def git(*args: str) -> None:
    subprocess.run(["git", *args], check=True, stdout=subprocess.DEVNULL)


def main(args: list[str]) -> int:
    mode = os.environ.get("FAKE_GH_MODE", "ok")
    log = os.environ.get("FAKE_GH_LOG")
    if log:
        with open(log, "a", encoding="utf-8") as stream:
            stream.write(" ".join(args) + "\n")
    if args[:1] == ["--version"]:
        print("gh version 0.0.0 (fake)")
        return 0
    if args[:2] == ["auth", "status"]:
        if mode == "unauthenticated":
            print("You are not logged into any GitHub hosts.", file=sys.stderr)
            return 1
        return 0
    if args[:2] == ["api", "user"]:
        if mode == "no-user":
            print("HTTP 401: Bad credentials", file=sys.stderr)
            return 1
        print(USER)
        return 0
    if args[:2] == ["repo", "create"]:
        if mode == "fail-create":
            print("GraphQL: could not create repository (fake failure)", file=sys.stderr)
            return 1
        remote = Path(os.environ["FAKE_GH_REMOTES"]) / f"{args[2]}.git"
        remote.parent.mkdir(parents=True, exist_ok=True)
        git("init", "--quiet", "--bare", "-b", "main", str(remote))
        git("remote", "add", "origin", str(remote))
        git("push", "--quiet", "-u", "origin", "HEAD")
        print(f"https://github.com/{args[2]}")
        return 0
    print(f"fake gh: unsupported arguments {args}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
