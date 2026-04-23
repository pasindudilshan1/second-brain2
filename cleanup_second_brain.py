#!/usr/bin/env python3
"""Remove obvious clutter from the second-brain project."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
from collections import defaultdict
from datetime import date
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
VAULT_DIR = PROJECT_ROOT / "second-brain"
ARTICLES_DIR = VAULT_DIR / "raw" / "articles"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def preferred_duplicate(files: list[Path]) -> Path:
    def score(path: Path) -> tuple[int, int, str]:
        numbered_suffix = bool(re.search(r"-\d+$", path.stem))
        return (1 if numbered_suffix else 0, len(path.name), path.name.lower())

    return sorted(files, key=score)[0]


def collect_targets() -> tuple[list[Path], list[Path], dict[str, list[Path]]]:
    files_to_delete: list[Path] = []
    dirs_to_delete: list[Path] = []
    duplicate_groups: dict[str, list[Path]] = {}

    for path in [PROJECT_ROOT / "__pycache__", VAULT_DIR / "__pycache__"]:
        if path.exists() and path.is_dir():
            dirs_to_delete.append(path)

    for path in [PROJECT_ROOT / "Untitled.base", PROJECT_ROOT / "Welcome.md", PROJECT_ROOT / "test_patch_file.txt"]:
        if path.exists() and path.is_file():
            files_to_delete.append(path)

    if ARTICLES_DIR.exists():
        article_files = [p for p in ARTICLES_DIR.iterdir() if p.is_file()]
        files_to_delete.extend(p for p in article_files if p.suffix.lower() in {".md", ".markdown"} and p.stat().st_size == 0)
        files_to_delete.extend(p for p in article_files if p.suffix.lower() not in {".md", ".markdown"})

        by_hash: dict[str, list[Path]] = defaultdict(list)
        for path in article_files:
            if path.suffix.lower() not in {".md", ".markdown"} or path.stat().st_size == 0:
                continue
            by_hash[file_hash(path)].append(path)

        for digest, paths in by_hash.items():
            if len(paths) < 2:
                continue
            keep = preferred_duplicate(paths)
            duplicates = [path for path in paths if path != keep]
            duplicate_groups[digest] = paths
            files_to_delete.extend(duplicates)

    # De-duplicate while preserving order.
    seen = set()
    unique_files = []
    for path in files_to_delete:
        if path not in seen:
            unique_files.append(path)
            seen.add(path)

    return unique_files, dirs_to_delete, duplicate_groups


def write_report(files: list[Path], dirs: list[Path], duplicate_groups: dict[str, list[Path]]) -> None:
    report_path = VAULT_DIR / "wiki" / "maps" / "cleanup-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        'title: "Cleanup Report"',
        "type: maintenance-report",
        "generated: cleanup-second-brain",
        f"created: {date.today().isoformat()}",
        "---",
        "",
        "# Cleanup Report",
        "",
        f"- Files removed: {len(files)}",
        f"- Directories removed: {len(dirs)}",
        f"- Duplicate content groups found: {len(duplicate_groups)}",
        "",
        "## Removed Files",
    ]
    if files:
        for path in files:
            lines.append(f"- `{path.relative_to(PROJECT_ROOT).as_posix()}`")
    else:
        lines.append("- None")

    lines.extend(["", "## Removed Directories"])
    if dirs:
        for path in dirs:
            lines.append(f"- `{path.relative_to(PROJECT_ROOT).as_posix()}`")
    else:
        lines.append("- None")

    lines.extend(["", "## Duplicate Groups"])
    if duplicate_groups:
        for paths in duplicate_groups.values():
            keep = preferred_duplicate(paths)
            lines.append(f"- Kept `{keep.relative_to(PROJECT_ROOT).as_posix()}`")
            for path in paths:
                if path != keep:
                    lines.append(f"  - Removed `{path.relative_to(PROJECT_ROOT).as_posix()}`")
    else:
        lines.append("- None")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Actually delete files. Without this, only preview.")
    args = parser.parse_args()

    files, dirs, duplicate_groups = collect_targets()
    print(f"Files selected:      {len(files)}")
    print(f"Directories selected:{len(dirs)}")
    print(f"Duplicate groups:    {len(duplicate_groups)}")

    for path in files[:30]:
        print(f"  file: {path}")
    if len(files) > 30:
        print(f"  ... {len(files) - 30} more files")
    for path in dirs:
        print(f"  dir:  {path}")

    if not args.apply:
        print("\nDry run only. Re-run with --apply to delete selected clutter.")
        return

    for path in files:
        if path.exists() and path.is_file():
            path.unlink()
    for path in dirs:
        if path.exists() and path.is_dir():
            shutil.rmtree(path)

    write_report(files, dirs, duplicate_groups)
    print("\nCleanup complete. Report written to second-brain/wiki/maps/cleanup-report.md")


if __name__ == "__main__":
    main()
