"""Create the verbatim files beside each port, and review_decisions.csv.

For every fmz_id in port_manifest.SIZING:
  ports/<slug>/original_source.md   byte copy of the corpus file
  ports/<slug>/original_sizing.txt  the listed line blocks, verbatim, labelled with line numbers
Copies only; the corpus file at the repository root is untouched.
"""
import csv
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from port_manifest import REJECTED_ON_READING, SIZING  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main():
    rows = {int(r['fmz_id']): r for r in csv.DictReader(open(ROOT / 'screening.csv', encoding='utf-8'))}
    for fid, blocks in SIZING.items():
        r = rows[fid]
        d = ROOT / 'ports' / r['slug']
        if not (d / 'module.py').exists():
            raise SystemExit(f'{d}/module.py missing')
        shutil.copyfile(ROOT / r['file'], d / 'original_source.md')
        lines = (ROOT / r['file']).read_text(encoding='utf-8').split('\n')
        out = [f"# Original sizing and money-management code, FMZ #{fid} ({r['name']})",
               f"# Source: {r['detail_url']}  (verbatim from original_source.md; line numbers refer to it)",
               "# Stored for later testing as a separate layer (criterion 4). Not part of the port's signals.",
               ""]
        for label, a, b in blocks:
            out.append(f"## {label}  [lines {a}-{b}]")
            out.extend(f"{i:>5}: {lines[i - 1]}" for i in range(a, b + 1))
            out.append("")
        (d / 'original_sizing.txt').write_text('\n'.join(out), encoding='utf-8')
    with open(ROOT / 'review_decisions.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['fmz_id', 'file', 'final_outcome', 'criterion', 'reason'])
        for fid, (crit, why) in sorted(REJECTED_ON_READING.items()):
            w.writerow([fid, rows[fid]['file'], 'REJECTED_ON_READING', crit, why])
        for fid in sorted(SIZING):
            w.writerow([fid, rows[fid]['file'], 'PORTED', '', f"ports/{rows[fid]['slug']}/"])
    print(len(SIZING), 'ports;', len(REJECTED_ON_READING), 'rejected on reading')


if __name__ == '__main__':
    main()
