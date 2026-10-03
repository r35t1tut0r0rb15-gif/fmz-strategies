"""Criterion 3: copy every crypto-exchange-only original into flagged/ with its reason.

Copies (never moves): the original stays at the repository root."""
import csv
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    rows = [r for r in csv.DictReader(open(ROOT / 'screening.csv', encoding='utf-8'))
            if r['overall'] == 'FLAGGED_CRYPTO_ONLY']
    for r in rows:
        d = ROOT / 'flagged' / r['slug']
        d.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / r['file'], d / 'original_source.md')
        kind = ('tool/library/monitor (not a signal strategy)'
                if r['c1'] == 'FAIL' and 'not a signal strategy' in r['c1_why'] else 'trading strategy/bot')
        (d / 'REASON.md').write_text(
            f"# {r['name']}\n\n"
            f"- FMZ id: {r['fmz_id']}\n- Source: {r['detail_url']} (repository copy: `{r['file']}`)\n"
            f"- Language: {r['lang']}\n- Author: {r['author']}\n- Last modified (FMZ): {r['last_modified']}\n"
            f"- Kind: {kind}\n\n"
            "## Why flagged (criterion 3: needs crypto-exchange-only features)\n\n"
            + ''.join(f"- {x}\n" for x in r['c3_why'].split(' | ') if x) +
            f"\n## Other screening notes\n\n- Criterion 1: {r['c1']} - {r['c1_why']}\n"
            f"- Duplicate group: {r['dup_group'] or 'none'}\n\n"
            "Not ported. Kept verbatim in `original_source.md` for future crypto-exchange work.\n",
            encoding='utf-8')
    print(len(rows), 'stored')


if __name__ == '__main__':
    main()
