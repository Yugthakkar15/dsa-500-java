"""Compile every solution with javac to make sure it builds.

Usage:  python scripts/check.py
Needs a JDK (javac) on your PATH. GitHub Actions runs the same check on every push.
Each solution compiles on its own, together with ListNode and TreeNode from src/_common.
"""
import shutil
import subprocess
import sys
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
COMMON = sorted(str(p) for p in (SRC / "_common").glob("*.java"))
PLACEHOLDER = "// Paste your accepted LeetCode solution here."


def main():
    if not shutil.which("javac"):
        sys.exit("javac not found. Install a JDK (17 or newer) and try again.")
    files = [p for p in sorted(SRC.glob("*/*/Solution.java")) if "_common" not in p.parts]
    failed = []
    checked = 0
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        if PLACEHOLDER in text:
            continue
        checked += 1
        # If the file defines its own ListNode/TreeNode (outside comments), skip the shared copy.
        code = re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.S)
        common = [c for c in COMMON
                  if not re.search(rf"\bclass\s+{Path(c).stem}\b", code)]
        with tempfile.TemporaryDirectory() as out:
            r = subprocess.run(["javac", "-nowarn", "-d", out, *common, str(f)],
                               capture_output=True, text=True)
        if r.returncode != 0:
            failed.append((f.relative_to(ROOT).as_posix(), r.stderr.strip()))
    for path, err in failed:
        print(f"\nFAILED  {path}\n{err}")
    print(f"\n{checked - len(failed)} of {checked} solutions compile.")
    if failed:
        print("Tip: LeetCode imports java.util.* for you; keep 'import java.util.*;' at the top of the file.")
        sys.exit(1)


if __name__ == "__main__":
    main()
