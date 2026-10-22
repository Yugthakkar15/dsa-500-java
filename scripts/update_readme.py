"""Rebuild README.md from the solutions in src/.

Usage:  python scripts/update_readme.py
GitHub Actions also runs this on every push, so the README stays current
even if you forget.
"""
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
PLACEHOLDER = "// Paste your accepted LeetCode solution here."
FIELD = re.compile(r"^\s*\*\s*(Difficulty|Topic|Solved on|Approach|Time|Space)\s*:\s*(.*)$")
TITLE = re.compile(r"^\s*\*\s*(\d+)\.\s+(.*)$")


def read_solution(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    if PLACEHOLDER in text:
        return None  # created but not solved yet
    info = {}
    for line in text.splitlines()[:25]:
        m = FIELD.match(line)
        if m:
            info[m.group(1)] = m.group(2).strip()
        t = TITLE.match(line)
        if t and "title" not in info:
            info["id"], info["title"] = int(t.group(1)), t.group(2).strip()
    return info


def badge(label, message, color):
    return (f"![{label}](https://img.shields.io/badge/"
            f"{quote(label.replace('-', '--'))}-{quote(message.replace('-', '--'))}-{color}?style=flat-square)")


def bar(done, total, width=12):
    filled = round(width * done / total) if total else 0
    pct = round(100 * done / total) if total else 0
    return "█" * filled + "░" * (width - filled) + f" {pct}%"


def cell(text):
    return (text or "").replace("|", "\\|").strip()


def main():
    data = json.loads((ROOT / "problems.json").read_text(encoding="utf-8"))
    topics = data["topics"]
    by_path = {}
    for p in data["problems"]:
        folder = topics[p["topic"]]["folder"]
        by_path[f"{folder}/{p['id']:04d}-{p['slug']}"] = p

    solved = []   # (problem-or-extra dict, info, relative path)
    for sol in sorted(SRC.glob("*/*/Solution.java")):
        rel = sol.parent.relative_to(SRC).as_posix()
        if rel.startswith("_common"):
            continue
        info = read_solution(sol)
        if info is None:
            continue
        p = by_path.get(rel)
        if p is None:  # extra problem outside the sheet
            slug = sol.parent.name
            p = {"id": info.get("id", 0), "slug": slug, "title": info.get("title", slug),
                 "difficulty": info.get("Difficulty", "?"), "topic": None, "companies": [], "order": 10**6}
        solved.append((p, info, sol.relative_to(ROOT).as_posix()))

    on_sheet = [s for s in solved if s[0]["topic"] is not None]
    extra = [s for s in solved if s[0]["topic"] is None]
    total = len(data["problems"])
    diff_total = Counter(p["difficulty"] for p in data["problems"])
    diff_done = Counter(s[0]["difficulty"] for s in on_sheet)
    company_done = Counter(c for s in on_sheet for c in s[0]["companies"])

    intro = (ROOT / "scripts" / "readme_intro.md").read_text(encoding="utf-8").strip()
    out = [intro, ""]
    out.append(" ".join([
        badge("solved", f"{len(on_sheet)} of {total}", "2F6FA3"),
        badge("easy", str(diff_done["Easy"]), "0E8A74"),
        badge("medium", str(diff_done["Medium"]), "C88A00"),
        badge("hard", str(diff_done["Hard"]), "C42B47"),
        badge("language", "Java", "E76F00"),
    ]))
    out += ["", "## Progress", "",
            "| Level | Solved | Progress |", "|---|---:|---|"]
    for d in ("Easy", "Medium", "Hard"):
        out.append(f"| {d} | {diff_done[d]} / {diff_total[d]} | `{bar(diff_done[d], diff_total[d])}` |")
    out.append(f"| **All** | **{len(on_sheet)} / {total}** | `{bar(len(on_sheet), total)}` |")

    out += ["", "## Topics", "", "| # | Topic | Solved | Progress |", "|---:|---|---:|---|"]
    for i, t in enumerate(topics):
        tot = sum(1 for p in data["problems"] if p["topic"] == i)
        done = sum(1 for s in on_sheet if s[0]["topic"] == i)
        name = f"[{t['name']}](#{anchor(t['name'])})" if done else t["name"]
        out.append(f"| {i + 1} | {name} | {done} / {tot} | `{bar(done, tot)}` |")

    if company_done:
        top = company_done.most_common(12)
        out += ["", "## Companies these problems come from", "",
                "Solved problems that each company has asked, based on LeetCode company tags.", "",
                " · ".join(f"**{c}** {n}" for c, n in top)]

    recent = sorted(solved, key=lambda s: s[1].get("Solved on", ""), reverse=True)[:10]
    if recent:
        out += ["", "## Recently solved", "", "| Date | Problem | Level | Topic |", "|---|---|---|---|"]
        for p, info, path in recent:
            tname = topics[p["topic"]]["name"] if p["topic"] is not None else "Extra"
            out.append(f"| {cell(info.get('Solved on'))} | [{p['id']}. {cell(p['title'])}]({path}) "
                       f"| {p['difficulty']} | {tname} |")

    out += ["", "## Solutions", ""]
    if not solved:
        out.append("_No solutions yet. The first one is on its way._")
    for i, t in enumerate(topics):
        rows = sorted((s for s in on_sheet if s[0]["topic"] == i), key=lambda s: s[0]["order"])
        if not rows:
            continue
        out += [f"### {t['name']}", "",
                "| # | Problem | Level | Approach | Time | Space | Code |", "|---:|---|---|---|---|---|---|"]
        for p, info, path in rows:
            out.append(f"| {p['id']} | [{cell(p['title'])}](https://leetcode.com/problems/{p['slug']}/) "
                       f"| {p['difficulty']} | {cell(info.get('Approach')) or '-'} | {cell(info.get('Time'))} "
                       f"| {cell(info.get('Space'))} | [Java]({path}) |")
        out.append("")
    if extra:
        out += ["### Extra problems", "", "| # | Problem | Level | Approach | Code |", "|---:|---|---|---|---|"]
        for p, info, path in sorted(extra, key=lambda s: s[2]):
            out.append(f"| {p['id'] or '-'} | [{cell(p['title'])}](https://leetcode.com/problems/{p['slug']}/) "
                       f"| {cell(info.get('Difficulty')) or '?'} | {cell(info.get('Approach')) or '-'} | [Java]({path}) |")
        out.append("")

    out += ["", "---", "",
            "<sub>This README is generated by `scripts/update_readme.py` from the solution files. "
            "The 500-problem list and company tags come from LeetCode company-wise question lists "
            "([source](https://github.com/liquidslr/leetcode-company-wise-problems)).</sub>", ""]
    (ROOT / "README.md").write_text("\n".join(out), encoding="utf-8")
    print(f"README updated: {len(on_sheet)}/{total} on the sheet, {len(extra)} extra.")


def anchor(name):
    return re.sub(r"[^a-z0-9 -]", "", name.lower()).replace(" ", "-")


if __name__ == "__main__":
    main()
