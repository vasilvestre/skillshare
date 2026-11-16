---
name: gitlab-review-fix
description: >
  Automatically fetch, analyze, and apply code review comments from GitLab merge
  requests. Use this skill whenever the user mentions fixing GitLab MR reviews,
  addressing code review comments, applying suggestions from a merge request,
  or working with glab and review feedback. Also trigger when the user wants to
  resolve discussions on an MR, process reviewer feedback, or auto-fix comments
  left by colleagues on GitLab. This skill handles suggestion blocks, interprets
  reviewer intent, commits changes locally, and reports what was fixed vs what
  needs human attention.
compatibility:
  tools: [Bash, Read, Edit, Write, Grep, Glob]
  dependencies: [glab >= 1.40, git, python3]
---

# GitLab Review Fix

Fetch unresolved code-review discussions from a GitLab merge request, interpret
reviewer feedback, apply safe automatic fixes, commit them locally, and report
what remains for human judgment.

## When to use

- The user pastes a GitLab MR URL and says "fix the reviews", "apply the
  comments", "address feedback", or similar.
- The user asks to work with the current branch's open MR.
- The user wants to batch-apply suggestion blocks from a GitLab MR.

## When NOT to use

- The user wants to create a new MR or merge an existing one (use glab directly).
- The user wants general GitLab project management (issues, pipelines, etc.).
- The MR has no unresolved discussions or the user explicitly says "just show me
  the comments" without wanting fixes applied.

## Workflow

### 1. Determine the target MR

The user can specify the MR in three ways. Try them in order:

1. **Explicit URL**: The user provides a full GitLab MR URL, e.g.
   `https://gitlab.com/owner/repo/-/merge_requests/123`.
2. **Explicit IID**: The user provides just the MR number, e.g. `!123` or `123`.
   Resolve the project from the current Git remote (`git remote get-url origin`).
3. **Current branch**: No MR specified. Detect the current branch with
   `git branch --show-current`, then find the open MR for that branch:
   ```bash
   glab mr list --source-branch="$(git branch --show-current)" --state=opened -F json
   ```
   If exactly one MR is returned, use it. If zero, tell the user there is no
   open MR for this branch. If more than one, ask the user which one.

Parse MR URLs with this regex (Python):
```python
import re
m = re.search(r'gitlab\.com/(.+?)/-/merge_requests/(\d+)', url)
project = m.group(1)  # e.g. "campingcarpark/si-main/octopus"
iid = m.group(2)      # e.g. "12659"
```

### 2. Fetch unresolved discussions

Use the GitLab REST API via `glab api` to get structured discussions with file
and line positions:

```bash
glab api "projects/<URL-encoded-project>/merge_requests/<IID>/discussions?per_page=100"
```

URL-encode the project path with Python:
```python
from urllib.parse import quote
encoded = quote(project, safe='')
```

Filter the JSON response:
- Keep only discussions where `resolvable == true` and `resolved == false`.
- Within each discussion, keep only notes where `system == false`.
- Skip general (`individual_note == true`) comments that have no file position
  unless they contain a ` ```suggestion ` block — those are rare but actionable.

For each kept note, extract:
- `note_id` (for later reference)
- `body` (the comment text)
- `author.username`
- `position.new_path` (file path in repo)
- `position.new_line` (target line number, 1-based)
- Any ` ```suggestion ` blocks inside `body`

### 3. Classify comments

Group comments into three buckets:

| Bucket | Criteria | Action |
|---|---|---|
| **Auto-fixable** | Contains a ` ```suggestion ` block, or is a clear mechanical fix (rename variable, remove unused import, fix typo, add type hint, etc.) | Apply immediately |
| **Interpretable** | Describes a concrete code change but without a suggestion block (e.g. "inject %kernel.project_dir% instead of Kernel") | Read surrounding code, infer the fix, apply if confident |
| **Needs human** | Open question, architectural debate, requires domain knowledge, or the fix is ambiguous | Skip and list for the user |

When in doubt, classify as **Needs human** — never guess on behavioral changes.

### 4. Parse and apply suggestion blocks

GitLab suggestion blocks follow this markdown pattern:

````markdown
```suggestion:-0+0
<replacement code>
```
````

The `:-0+0` suffix indicates the line range to replace. The numbers after `-`
and `+` are line counts relative to the commented line. In practice, for a
single-line replacement the block contains exactly the new line(s) that should
replace the target line.

Use the bundled script `scripts/apply_suggestions.py` to apply suggestion blocks
safely:

```bash
python3 scripts/apply_suggestions.py <discussions.json> <repo-root>
```

The script:
1. Reads the discussions JSON.
2. For each suggestion block, replaces the line at `position.new_line` in
   `position.new_path` with the suggested code.
3. Warns if the current file content at that line does not match the expected
   original (suggestion blocks don't include the original, so we trust the line
   number).
4. Writes modified files in-place.
5. Outputs a JSON report of what was changed.

If the script is missing, inline its logic (see script source for reference).

### 5. Apply interpretable comments

For comments without suggestion blocks but that describe a concrete change:

1. Read the file at `position.new_path` around `position.new_line` (±5 lines).
2. Understand the reviewer intent from `body`.
3. Make the minimal edit that satisfies the comment.
4. If the fix spans multiple files or requires refactoring, treat it as
   **Needs human** instead.

Examples of safe interpretable fixes:
- "Inject X instead of Y" → change constructor parameter and assignment.
- "Use yield instead of collecting in array" → replace array push with yield.
- "This variable is unused" → remove the variable.
- "Missing return type" → add the return type declaration.

### 6. Commit locally

After all auto-fixable and interpretable comments are applied:

1. Stage the modified files with `git add`.
2. Create a commit with a descriptive message that references the MR:
   ```bash
   git commit -m "Apply review feedback from MR !<IID>" \
              -m "Auto-fixed <N> comment(s):" \
              -m "- <author>: <short summary of each fix>"
   ```
3. **Do NOT push.** The user asked to commit locally only.

### 7. Report results

Present a structured summary:

```markdown
# MR !<IID> Review Fix Report

## Applied (<count>)
| File | Line | Author | Action |
|---|---|---|---|
| ... | ... | ... | ... |

## Needs Human Attention (<count>)
| File | Line | Author | Comment | Why skipped |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## Already Resolved (<count>)
... (list if any were already resolved before we started)
```

For each applied fix, include a one-line description of what changed.
For each skipped comment, explain why (question, ambiguous, too large, etc.).

## Important Rules

- **Never push.** Only stage and commit locally.
- **Never resolve discussions on GitLab.** That is the user's decision after
  they review the changes.
- **Preserve code style.** Match indentation, quotes, and naming conventions of
  the surrounding file.
- **One fix per logical change.** If two comments affect the same line, apply
  both and test mentally that they don't conflict.
- **Fail safe.** If a file has uncommitted changes before you start, warn the
  user and ask whether to stash, abort, or proceed.
- **Output artifacts can be written outside the repo.** If the task asks you to
  save a summary, diff, or other report to a specific path, write it there even
  if the path is outside the repository. This rule applies only to output
  reports, never to code changes.

## Bundled Scripts

### `scripts/apply_suggestions.py`

Reads a GitLab discussions JSON file and applies suggestion blocks to the local
repository. See script header for usage.
