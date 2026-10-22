"""Fail-fast checks for files intended for a future public Git repository."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXCLUDED_PARTS = {"review_required", "outputs", ".git", "__pycache__"}
TEXT_SUFFIXES = {".py", ".r", ".md", ".txt", ".yml", ".yaml", ".json", ".cff", ".tsv", ".csv", ".ps1"}
ABSOLUTE_PATH = re.compile(
    r"(?:(?<![A-Za-z])[A-Za-z]:[\\/](?!Windows[\\/]Fonts)|(?<![A-Za-z0-9:])\/(?:home|Users)\/)"
)
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "generic assignment": re.compile(r"(?i)(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
}


def public_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and not any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts)
        and path.suffix.lower() in TEXT_SUFFIXES
    ]


def main() -> int:
    findings: list[str] = []
    for path in public_files():
        if path.name == Path(__file__).name:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = path.relative_to(ROOT)
        for line_number, line in enumerate(text.splitlines(), start=1):
            if ABSOLUTE_PATH.search(line):
                findings.append(f"absolute path: {relative}:{line_number}: {line.strip()}")
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(line):
                    findings.append(f"{label}: {relative}:{line_number}")
    if findings:
        print("Preflight findings:")
        print("\n".join(findings))
        return 1
    print(f"Preflight passed for {len(public_files())} public text files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
