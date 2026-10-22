# How to use this repo

## Every time you solve a problem

1. **Create the file** (run from the repo folder in the VS Code terminal):

   ```powershell
   py -3.12 scripts/new.py next      # the next problem in sheet order
   py -3.12 scripts/new.py 1         # or a specific LeetCode number
   py -3.12 scripts/new.py two-sum   # or the slug from the LeetCode URL
   ```

   This creates `src/<topic>/<number>-<slug>/Solution.java` with the title, link, difficulty, topic and companies already filled in.

2. **Solve it on LeetCode in Java.** When it's accepted, paste your code into the file, replacing the line
   `// Paste your accepted LeetCode solution here.`

3. **Fill in three lines** in the header: `Approach`, `Time` and `Space`. One line each is enough, for example:

   ```
   * Approach   : HashMap of value -> index; for each x look up target - x
   * Time       : O(n)
   * Space      : O(n)
   ```

   Recruiters read these. They show you understand the solution, not just that you pasted it.

4. **Commit and push:**

   ```powershell
   git add .
   git commit -m "Solve 1. Two Sum"
   git push
   ```

   GitHub then updates the README progress tables for you within a minute or two, and checks that every solution compiles.

5. **Tick it off on your DSA 500 Sheet website** so your streak and daily checklist stay in sync.

## Optional checks on your own computer

```powershell
py -3.12 scripts/update_readme.py   # rebuild README.md now instead of waiting for GitHub
py -3.12 scripts/check.py           # compile every solution (needs a JDK, version 17 or newer)
```

After GitHub's README update, run `git pull` before your next push so your copy has the new README.

## Good to know

- A file still containing the "Paste your accepted LeetCode solution here" line counts as **not solved**, so half-done work never inflates your numbers.
- `ListNode` and `TreeNode` are already defined in `src/_common/`, exactly as on LeetCode. Leave LeetCode's commented-out definitions as comments.
- A few problems (Clone Graph, Copy List with Random Pointer, Populating Next Right Pointers, Flatten a Multilevel Doubly Linked List, Find in Mountain Array) need LeetCode's own `Node` or `MountainArray` class. `new.py` adds it to the file for you.
- **Design problems** (LRU Cache, Min Stack…): replace `class Solution` with the class LeetCode gives you, e.g. `class LRUCache`.
- **Problems that aren't on the sheet** still work: `py -3.12 scripts/new.py some-problem-slug` puts them in `src/30-extra/`. Fill in the difficulty yourself.
- To change the top of the README (your name, links), edit `scripts/readme_intro.md`, not README.md, because README.md is regenerated.
- Commit little and often. A green contribution graph with daily commits is part of what recruiters notice.
