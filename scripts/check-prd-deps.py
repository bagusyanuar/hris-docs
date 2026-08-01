#!/usr/bin/env python3
"""
Cross-check `depends_on` / `consumed_by` symmetry across all PRD/*.md files.

A PRD's frontmatter declares two directed edges:
  depends_on: [module_a@1.0.0, ...]   -- this module consumes module_a
  consumed_by: [module_c@planned, ...] -- module_c consumes this module

These two lists are maintained by hand (see scaffold-prd skill, section
"Updating an Existing PRD" step 6 - "Ripple-check dependents"). Nothing
regenerates them automatically, so they drift. This script finds the drift:

  1. Missing reverse edge: A depends_on B, but B's consumed_by doesn't list A.
  2. Missing forward edge: B's consumed_by lists A, but A has no depends_on B.
  3. Stale version pointer: A depends_on B@x, but B's own frontmatter version
     is currently y != x (A may be relying on an outdated contract).
  4. Unknown target: an edge points to a module slug with no PRD/<slug>.md
     file. Not always an error - some modules aren't migrated to hris-docs
     yet (see PRD/README.md "Belum dimigrasi") - reported as a warning, not
     a failure.

Usage:
    python3 scripts/check-prd-deps.py
    python3 scripts/check-prd-deps.py --prd-dir /path/to/PRD

Exit code is non-zero if any missing-edge or stale-version issue is found
(unknown-target warnings alone do not fail the run).
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
# module@version, version may contain dots or be a bare word like "planned"
EDGE_RE = re.compile(r"([a-zA-Z0-9_-]+)@([a-zA-Z0-9_.]+)")

SKIP_FILES = {"_TEMPLATE.md", "README.md"}


@dataclass
class Prd:
    slug: str
    path: Path
    module: str = ""
    version: str = ""
    depends_on: dict = field(default_factory=dict)   # slug -> version string as declared
    consumed_by: dict = field(default_factory=dict)  # slug -> version string as declared


def parse_frontmatter_field(fm: str, key: str) -> str:
    m = re.search(rf"^{key}:\s*(.*)$", fm, re.MULTILINE)
    return m.group(1).strip() if m else ""


def parse_edges(raw: str) -> dict:
    """Extract {slug: version} pairs from a `[a@1.0.0, b@planned]` style value."""
    return {slug: version for slug, version in EDGE_RE.findall(raw)}


def load_prds(prd_dir: Path) -> dict:
    prds = {}
    for path in sorted(prd_dir.glob("*.md")):
        if path.name in SKIP_FILES:
            continue
        text = path.read_text(encoding="utf-8")
        m = FRONTMATTER_RE.match(text)
        if not m:
            print(f"WARN  {path.name}: no frontmatter block found, skipping")
            continue
        fm = m.group(1)
        slug = path.stem
        prd = Prd(
            slug=slug,
            path=path,
            module=parse_frontmatter_field(fm, "module"),
            version=parse_frontmatter_field(fm, "version"),
            depends_on=parse_edges(parse_frontmatter_field(fm, "depends_on")),
            consumed_by=parse_edges(parse_frontmatter_field(fm, "consumed_by")),
        )
        prds[slug] = prd
    return prds


def check(prds: dict) -> int:
    issues = 0
    warnings = 0

    for slug, prd in prds.items():
        # depends_on -> reverse edge must exist in target's consumed_by
        for target_slug, declared_version in prd.depends_on.items():
            target = prds.get(target_slug)
            if target is None:
                print(f"WARN  {prd.path.name}: depends_on '{target_slug}' "
                      f"has no PRD/{target_slug}.md locally (may not be migrated yet)")
                warnings += 1
                continue

            if slug not in target.consumed_by:
                print(f"FAIL  {prd.path.name}: depends_on {target_slug}@{declared_version}, "
                      f"but {target.path.name} consumed_by is missing '{slug}'")
                issues += 1

            if target.version and declared_version not in ("planned", target.version):
                print(f"FAIL  {prd.path.name}: depends_on {target_slug}@{declared_version}, "
                      f"but {target.path.name} is currently at version {target.version} "
                      f"(stale pointer - re-verify the referenced section still holds)")
                issues += 1

        # consumed_by -> forward edge must exist in consumer's depends_on
        for consumer_slug, declared_version in prd.consumed_by.items():
            consumer = prds.get(consumer_slug)
            if consumer is None:
                print(f"WARN  {prd.path.name}: consumed_by '{consumer_slug}' "
                      f"has no PRD/{consumer_slug}.md locally (may not be migrated yet)")
                warnings += 1
                continue

            if slug not in consumer.depends_on:
                print(f"FAIL  {prd.path.name}: consumed_by lists {consumer_slug}, "
                      f"but {consumer.path.name} has no depends_on '{slug}'")
                issues += 1

    print()
    print(f"{len(prds)} PRD(s) checked, {issues} issue(s), {warnings} warning(s)")
    return 1 if issues else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prd-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "PRD",
        help="Path to the PRD/ directory (default: ../PRD relative to this script)",
    )
    args = parser.parse_args()

    if not args.prd_dir.is_dir():
        print(f"error: {args.prd_dir} is not a directory", file=sys.stderr)
        return 2

    prds = load_prds(args.prd_dir)
    return check(prds)


if __name__ == "__main__":
    raise SystemExit(main())
