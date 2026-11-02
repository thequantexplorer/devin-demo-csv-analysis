"""Check that reports/ has a short findings note and the charts it links to.

Usage: python3 scripts/check_reports.py   (exit code 0 = pass, 1 = fail)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
NOTE = REPORTS / "findings.md"
MAX_WORDS = 600
MIN_CHARTS = 2


def main():
    problems = []
    if not NOTE.is_file():
        print(f"FAIL: {NOTE.relative_to(ROOT)} not found. Nobody has analyzed data/orders.csv yet.")
        return 1

    text = NOTE.read_text(encoding="utf-8")
    words = len(text.split())
    if words > MAX_WORDS:
        problems.append(f"findings.md has {words} words; keep it under {MAX_WORDS}.")

    linked = re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", text)
    charts = [p for p in linked if p.lower().endswith((".png", ".svg"))]
    if len(charts) < MIN_CHARTS:
        problems.append(f"findings.md shows {len(charts)} chart(s) with ![...](file.png); it needs at least {MIN_CHARTS}.")
    for chart in charts:
        path = (NOTE.parent / chart).resolve()
        if not path.is_file() or path.stat().st_size == 0:
            problems.append(f"chart {chart} is linked from findings.md but is missing or empty.")
        elif REPORTS not in path.parents:
            problems.append(f"chart {chart} must live inside reports/.")

    for p in problems:
        print(f"FAIL: {p}")
    if problems:
        return 1
    print(f"OK: findings.md ({words} words) with {len(charts)} charts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
