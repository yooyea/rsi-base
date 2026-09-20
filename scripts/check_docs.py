#!/usr/bin/env python3
"""Check this repository's simple inline local links and document structure.

This is not a general Markdown parser. External URLs, anchor existence,
reference-style links and semantic correctness are outside its scope.
Rule sections must contain prose, and every rule must be reachable from SKILL.md.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

HEADINGS = ("保障目标", "适用条件", "工程落实", "有效性验证", "边界")
LINK = re.compile(r"\[[^\]\n]+\]\(([^)\n]+)\)")


def prose_lines(text: str):
    """Ignore fenced examples and single-backtick inline examples."""
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            yield number, re.sub(r"`[^`]*`", "", line)


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors = []
    for required in ("README.md", "AGENTS.md", "SKILL.md"):
        if not (root / required).is_file():
            errors.append(f"Missing entry document: {required}")
    rule_root = root / "chapters/engineering/rules"
    graph: dict[Path, set[Path]] = {}
    rules = set(rule_root.rglob("*.md"))
    if not rules:
        errors.append("No engineering rules found")
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if ".git" in relative.parts:
            continue
        if not path.resolve().is_relative_to(root):
            errors.append(f"{relative}: document escapes repository")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{relative}: cannot read UTF-8: {exc}")
            continue
        if not text.strip():
            errors.append(f"{relative}: empty document")
        if path == root / "SKILL.md":
            front = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
            if front is None:
                errors.append("SKILL.md: missing frontmatter")
            else:
                for field in ("name", "description"):
                    if not re.search(rf"^{field}:[ \t]*\S[^\n]*$", front.group(1), re.M):
                        errors.append(f"SKILL.md: missing {field}")
        graph[path] = set()
        prose = list(prose_lines(text))
        if path.is_relative_to(rule_root):
            present = {line.strip() for _, line in prose}
            for heading in HEADINGS:
                if f"## {heading}" not in present:
                    errors.append(f"{relative}: missing section {heading}")
            section = None
            bodies: dict[str, list[str]] = {}
            for _, line in prose:
                if line.startswith("## "):
                    section = line[3:].strip()
                    bodies.setdefault(section, [])
                elif section is not None and line.strip() and not line.lstrip().startswith("#"):
                    bodies[section].append(line)
            for heading in HEADINGS:
                if f"## {heading}" in present and not bodies.get(heading):
                    errors.append(f"{relative}: empty section {heading}")
        for number, line in prose:
            for match in LINK.finditer(line):
                href = match.group(1).strip().strip("<>")
                if href.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                local = href.split("#", 1)[0]
                target = (path.parent / local).resolve()
                if not target.is_relative_to(root):
                    errors.append(f"{relative}:{number}: link escapes repository: {href}")
                elif not target.exists():
                    errors.append(f"{relative}:{number}: missing local target: {href}")
                elif target.is_file() and target.suffix == ".md":
                    graph[path].add(target)
    reachable: set[Path] = set()
    pending = [root / "SKILL.md"]
    while pending:
        current = pending.pop()
        if current not in reachable:
            reachable.add(current)
            pending.extend(graph.get(current, ()))
    for path in sorted(rules - reachable):
        errors.append(f"{path.relative_to(root)}: rule is not reachable from SKILL.md")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        print("\n".join(errors))
        return 1
    print("Local document paths and required structure passed; semantic correctness is not assessed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
