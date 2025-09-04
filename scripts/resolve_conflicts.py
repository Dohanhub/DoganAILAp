#!/usr/bin/env python3
"""
Resolve git conflict markers in text files by keeping the HEAD section.
Only processes files under provided roots (defaults to 'src').

Behavior:
- For each conflict block:
  <<<<<<< HEAD
  ... KEEP THIS ...
  =======
  ... DROP THIS ...
  >>>>>>> some-commit-or-branch
  The script keeps the top section and removes markers and the bottom.
- If a block has no ======= (rare), it keeps the content between <<<<<<< and >>>>>>>.

Use with caution. Review diffs after running.
"""
from __future__ import annotations
import sys
from pathlib import Path

MARK_A = "<<<<<<< HEAD"
MARK_B = "======="
MARK_C = ">>>>>>>"

def resolve_text(text: str) -> str:
    out_lines: list[str] = []
    lines = text.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.startswith(MARK_A):
            # collect head section until MARK_B, then skip until MARK_C
            i += 1
            head: list[str] = []
            # capture head
            while i < n and not lines[i].startswith(MARK_B) and not lines[i].startswith(MARK_C):
                head.append(lines[i])
                i += 1
            # skip separator if present
            if i < n and lines[i].startswith(MARK_B):
                i += 1
                # skip bottom until MARK_C
                while i < n and not lines[i].startswith(MARK_C):
                    i += 1
            # skip closing marker if present
            if i < n and lines[i].startswith(MARK_C):
                i += 1
            out_lines.extend(head)
            continue
        else:
            out_lines.append(line)
            i += 1
    # preserve trailing newline if original had it
    return "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")

def process_file(path: Path) -> bool:
    try:
        data = path.read_text(encoding="utf-8", errors="strict")
    except Exception:
        try:
            data = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return False
    if MARK_A not in data and MARK_C not in data:
        return False
    new = resolve_text(data)
    if new != data:
        path.write_text(new, encoding="utf-8")
        return True
    return False

def main(argv: list[str]) -> int:
    roots = [Path(p) for p in (argv[1:] if len(argv) > 1 else ["src"]) ]
    changed = 0
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            # Skip virtualenvs or binary assets
            pstr = str(path).lower()
            if any(seg in pstr for seg in (".venv", ".git", "node_modules", "__pycache__")):
                continue
            try:
                if process_file(path):
                    changed += 1
            except Exception:
                continue
    print(f"Resolved conflict markers in {changed} files.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

