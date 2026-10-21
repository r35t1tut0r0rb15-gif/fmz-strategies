"""Store one crypto-exchange-only id found on reading (rule C7): copy the corpus file to flagged/<slug>/original_source.md
and write REASON.md (LF), same layout as store_flagged.py. Copies only; refuses to overwrite.
Usage: python -X utf8 -I _flag_one.py <fmz_id> <reason text>"""
import csv
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]  # repository root (cloud copy, 2026-10-21)


def main():
    fid, why = sys.argv[1], sys.argv[2]
    r = next(x for x in csv.DictReader(open(REPO / "screening.csv", encoding="utf-8")) if x["fmz_id"] == fid)
    d = REPO / "flagged" / r["slug"]
    if d.exists():
        raise SystemExit(f"refused: {d} exists")
    d.mkdir(parents=True)
    shutil.copyfile(REPO / r["file"], d / "original_source.md")
    text = (f"# {r['name']}\n\n"
            f"- FMZ id: {fid}\n- Source: {r['detail_url']} (repository copy: `{r['file']}`)\n"
            f"- Language: {r['lang']}\n- Author: {r['author']}\n- Last modified (FMZ): {r['last_modified']}\n"
            "- Kind: trading strategy/bot\n\n"
            "## Why flagged (criterion 3: needs crypto-exchange-only features; found on reading, FMZ-C cloud)\n\n"
            f"- {why}\n\n"
            "Not ported. Kept verbatim in `original_source.md` for future crypto-exchange work.\n")
    (d / "REASON.md").write_bytes(text.encode("utf-8"))
    print("flagged", d.name)


if __name__ == "__main__":
    main()
