"""Print the code part of corpus files (Name, Author, Arguments, Source with line numbers, Last Modified).
Descriptions are skipped (criterion 7: FMZ's claims are ignored). Read only.
Usage: python -X utf8 -I show_src.py <fmz_id> [<fmz_id> ...]"""
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]  # repository root (cloud copy, 2026-10-21)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import heartbeat  # noqa: E402



def main():
    heartbeat.beat(Path(__file__).name)
    rows = {r["fmz_id"]: r for r in csv.DictReader(open(REPO / "screening.csv", encoding="utf-8"))}
    for fid in sys.argv[1:]:
        r = rows[fid]
        lines = (REPO / r["file"]).read_bytes().decode("utf-8").split("\n")
        print(f"======== {fid} | {r['name']} | {r['author']} | {r['lang']} | {r['last_modified']} | {r['slug']}")
        start = next((i for i, l in enumerate(lines) if l.startswith("> Strategy Arguments")), None)
        if start is None:
            start = next((i for i, l in enumerate(lines) if l.startswith("> Source")), 0)
        for i in range(start, len(lines)):
            s = lines[i].rstrip()
            if s.startswith("> Detail"):
                break
            if s:
                print(f"{i + 1:>4}: {s}")


if __name__ == "__main__":
    main()
