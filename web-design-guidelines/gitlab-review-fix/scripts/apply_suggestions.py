#!/usr/bin/env python3
"""
apply_suggestions.py

Reads GitLab MR discussions JSON (from glab api) and applies suggestion blocks
to files in a local repository.

Usage:
    python3 apply_suggestions.py discussions.json /path/to/repo

Outputs a JSON report to stdout describing what was changed.
"""

import json
import re
import sys
from pathlib import Path


def extract_suggestions(body: str) -> list[str]:
    pattern = re.compile(r"```suggestion[^\n]*\n(.*?)\n```", re.DOTALL)
    return pattern.findall(body)


def apply_change(file_path: Path, line_number: int, replacement_lines: list[str]) -> dict:
    if not file_path.exists():
        return {
            "status": "error",
            "reason": f"File not found: {file_path}",
        }

    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    if line_number < 1 or line_number > len(lines):
        return {
            "status": "error",
            "reason": f"Line {line_number} out of range (file has {len(lines)} lines)",
        }

    original_line = lines[line_number - 1]
    ends_with_newline = original_line.endswith("\n")

    normalized_replacement = []
    for index, replacement_line in enumerate(replacement_lines):
        is_last_line = index == len(replacement_lines) - 1
        if is_last_line and ends_with_newline and not replacement_line.endswith("\n"):
            replacement_line += "\n"
        normalized_replacement.append(replacement_line)

    new_lines = lines[:line_number - 1] + normalized_replacement + lines[line_number:]
    file_path.write_text("".join(new_lines), encoding="utf-8")

    return {
        "status": "applied",
        "original_line": original_line.rstrip("\n"),
        "replacement": [line.rstrip("\n") for line in normalized_replacement],
    }


def process_discussions(discussions: list[dict], repo_root: Path) -> list[dict]:
    results = []

    for discussion in discussions:
        if not discussion.get("resolvable") or discussion.get("resolved"):
            continue

        for note in discussion.get("notes", []):
            if note.get("system"):
                continue

            body = note.get("body", "")
            suggestions = extract_suggestions(body)

            if not suggestions:
                continue

            position = note.get("position", {})
            new_path = position.get("new_path")
            new_line = position.get("new_line")

            if not new_path or new_line is None:
                results.append({
                    "discussion_id": discussion.get("id"),
                    "note_id": note.get("id"),
                    "status": "skipped",
                    "reason": "No file position in note",
                })
                continue

            file_path = repo_root / new_path
            replacement_lines = suggestions[0].splitlines()

            result = apply_change(file_path, new_line, replacement_lines)
            results.append({
                "discussion_id": discussion.get("id"),
                "note_id": note.get("id"),
                "file": new_path,
                "line": new_line,
                "author": note.get("author", {}).get("username"),
                **result,
            })

    return results


def main() -> int:
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <discussions.json> <repo-root>", file=sys.stderr)
        return 1

    discussions_path = Path(sys.argv[1])
    repo_root = Path(sys.argv[2]).resolve()

    discussions = json.loads(discussions_path.read_text(encoding="utf-8"))
    if not isinstance(discussions, list):
        print("Error: discussions.json must contain a JSON array", file=sys.stderr)
        return 1

    results = process_discussions(discussions, repo_root)
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
