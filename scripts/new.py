"""Create the file for a problem you are about to solve.

Usage (from the repo folder):
    python scripts/new.py 1                 # by LeetCode number
    python scripts/new.py two-sum           # by the slug in the LeetCode URL
    python scripts/new.py https://leetcode.com/problems/two-sum/
    python scripts/new.py next              # the next unsolved problem in sheet order

It creates src/<topic>/<number>-<slug>/Solution.java with a filled-in header.
Paste your accepted LeetCode code into it, fill in Approach / Time / Space,
then commit and push.
"""
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
PLACEHOLDER = "// Paste your accepted LeetCode solution here."

# Problems whose LeetCode code uses a custom class you must keep in the file.
EXTRA_DEFS = {
    "copy-list-with-random-pointer": """class Node {
    int val;
    Node next;
    Node random;

    public Node(int val) {
        this.val = val;
        this.next = null;
        this.random = null;
    }
}""",
    "clone-graph": """class Node {
    public int val;
    public List<Node> neighbors;
    public Node() { val = 0; neighbors = new ArrayList<Node>(); }
    public Node(int _val) { val = _val; neighbors = new ArrayList<Node>(); }
    public Node(int _val, ArrayList<Node> _neighbors) { val = _val; neighbors = _neighbors; }
}""",
    "populating-next-right-pointers-in-each-node": """class Node {
    public int val;
    public Node left;
    public Node right;
    public Node next;

    public Node() {}
    public Node(int _val) { val = _val; }
    public Node(int _val, Node _left, Node _right, Node _next) {
        val = _val; left = _left; right = _right; next = _next;
    }
}""",
    "flatten-a-multilevel-doubly-linked-list": """class Node {
    public int val;
    public Node prev;
    public Node next;
    public Node child;
}""",
    "find-in-mountain-array": """interface MountainArray {
    int get(int index);
    int length();
}""",
}


def load():
    with open(ROOT / "problems.json", encoding="utf-8") as f:
        return json.load(f)


def solution_path(data, p):
    folder = data["topics"][p["topic"]]["folder"]
    return SRC / folder / f"{p['id']:04d}-{p['slug']}" / "Solution.java"


def find(data, arg):
    arg = arg.strip().rstrip("/")
    if arg.lower() == "next":
        for p in data["problems"]:
            if not solution_path(data, p).exists():
                return p
        sys.exit("Every problem on the sheet already has a file. Nice work.")
    m = re.search(r"leetcode\.com/problems/([a-z0-9-]+)", arg)
    if m:
        arg = m.group(1)
    for p in data["problems"]:
        if arg.isdigit() and p["id"] == int(arg):
            return p
        if p["slug"] == arg.lower():
            return p
    return None


def header(p, topic_name):
    today = datetime.date.today().isoformat()
    cos = p.get("companies", [])
    companies = ", ".join(cos[:8]) if cos else "-"
    if len(cos) > 8:
        companies += f" (+{len(cos) - 8} more)"
    return f"""/*
 * {p['id']}. {p['title']}
 * https://leetcode.com/problems/{p['slug']}/
 *
 * Difficulty : {p['difficulty']}
 * Topic      : {topic_name}
 * Asked by   : {companies}
 * Solved on  : {today}
 *
 * Approach   :
 * Time       : O()
 * Space      : O()
 */
"""


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    data = load()
    arg = " ".join(sys.argv[1:])
    p = find(data, arg)
    if p is None:
        # Not on the 500 sheet: put it in an "extra" folder.
        slug = arg.lower().strip().rstrip("/").split("/")[-1]
        if not re.fullmatch(r"[a-z0-9-]+", slug) or slug.isdigit():
            sys.exit("That problem is not on the sheet. Run it with the slug instead, e.g. "
                     "python scripts/new.py lru-cache")
        title = slug.replace("-", " ").title()
        p = {"id": 0, "slug": slug, "title": title, "difficulty": "?", "companies": [], "topic": None}
        path = SRC / "30-extra" / slug / "Solution.java"
        topic_name = "Extra (not on the sheet)"
    else:
        path = solution_path(data, p)
        topic_name = data["topics"][p["topic"]]["name"]

    if path.exists():
        print(f"Already exists: {path.relative_to(ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    body = header(p, topic_name) + "import java.util.*;\n\n"
    if p["slug"] in EXTRA_DEFS:
        body += "// LeetCode defines this class for you; it is kept here so the file compiles.\n"
        body += EXTRA_DEFS[p["slug"]] + "\n\n"
    body += "class Solution {\n    " + PLACEHOLDER + "\n}\n"
    path.write_text(body, encoding="utf-8")
    print(f"Created {path.relative_to(ROOT)}")
    print(f"Open:   https://leetcode.com/problems/{p['slug']}/")
    if p["topic"] is not None and data["topics"][p["topic"]]["name"] == "Design":
        print("Design problem: replace 'class Solution' with the class LeetCode gives you (e.g. LRUCache).")


if __name__ == "__main__":
    main()
