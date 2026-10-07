"""Near-duplicate groups for the porting queue (rule 7, 2026-10-07). Static text comparison only.

Population: the 3,747 remaining PORT_CANDIDATE rows (screening.csv overall == PORT_CANDIDATE and
no entry in review_decisions.csv), both workers' halves (A: fmz_id < 439378, B: >= 439378).

Normalisation (identical to screen.py's criterion 6): comments removed (screen.strip_code);
strings -> S; plot/label/alert/fill lines and cosmetic keyword arguments removed; every number
-> 0; 5-token shingles (screen.shingles). Similarity = exact Jaccard |A & B| / |A | B|, same
language only.

Two kinds of group are written, both keyed so a port can quote its group id (rule 7):

kind near_duplicate_ge_0.80, group_id "DG<representative id>"
    The screen's duplicates.csv groups (union-find over pairs at Jaccard >= 0.80, run over all
    5,806 files). The candidate in such a group is its representative; the other members are the
    rows the screen set to DUPLICATE (or REJECTED / FLAGGED_CRYPTO_ONLY on their own merits). All
    members are listed, with their `overall`, so rule 7 can be applied to them.
    The exhaustive check below found NO pair of remaining candidates at >= 0.80, which confirms
    that the screen's pruned candidate generation missed none among candidates.

kind similar_0.65_to_0.80, group_id "ND<lowest fmz_id>"
    EXHAUSTIVE check over all 3,747 candidates: exact Jaccard for every same-language pair whose
    shingle-set sizes allow Jaccard >= 0.65 (min/max size ratio >= 0.65; other pairs are below
    0.65 by construction). Pairs at >= 0.65 are merged by union-find (transitive).

exact_duplicate_of: lowest fmz_id in the group whose code is identical after comment removal and
deletion of all whitespace (numbers and strings kept), else ''. Exact duplicates stay set aside;
near-duplicates are ported with their group id.

Output: near_duplicate_groups.csv (one row per file per group; a candidate can be in one group of
each kind).
"""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fmzparse import parse  # noqa: E402
from screen import shingles, strip_code  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
THRESHOLD = 0.80   # near-duplicate (screen criterion 6 level)
FLOOR = 0.65       # lowest Jaccard grouped here (screen possible_duplicates level)
SPLIT = 439378     # worker B ports ids >= SPLIT


def load(r):
    p = parse(ROOT / r['file'])
    lang = p['lang'].lower()
    code = strip_code(p['code'], 'python' if lang == 'python' else ('pine' if lang == 'pinescript' else lang))
    return {'id': int(r['fmz_id']), 'lang': r['lang'], 'file': r['file'], 'overall': r['overall'],
            'sh': shingles(code, 5), 'exact': re.sub(r'\s+', '', code)}


def jaccard(a, b):
    inter = len(a & b)
    return inter / (len(a) + len(b) - inter) if (a or b) else 1.0


def emit(out, kind, gid, members, best):
    members = sorted(members, key=lambda d: d['id'])
    first_exact = {}
    n_a = sum(d['id'] < SPLIT for d in members)
    for d in members:
        ex = first_exact.setdefault(d['exact'], d['id'])
        jac, partner = best[d['id']]
        out.append({'group_id': gid, 'kind': kind, 'fmz_id': d['id'], 'lang': d['lang'],
                    'half': 'A' if d['id'] < SPLIT else 'B', 'overall': d['overall'],
                    'n_members': len(members), 'members_in_A': n_a, 'members_in_B': len(members) - n_a,
                    'best_partner_id': partner, 'best_jaccard': f'{jac:.3f}',
                    'exact_duplicate_of': '' if ex == d['id'] else ex, 'file': d['file']})


def main():
    rows = list(csv.DictReader(open(ROOT / 'screening.csv', encoding='utf-8')))
    byid = {r['fmz_id']: r for r in rows}
    decided = {r['fmz_id']: r['final_outcome']
               for r in csv.DictReader(open(ROOT / 'review_decisions.csv', encoding='utf-8'))}
    cand = [load(r) for r in rows if r['overall'] == 'PORT_CANDIDATE' and r['fmz_id'] not in decided]
    print(len(cand), 'candidates')
    out = []

    # kind 1: the screen's >= 0.80 groups, every member, best partner recomputed exactly
    ngroups1 = 0
    for g in csv.DictReader(open(ROOT / 'duplicates.csv', encoding='utf-8')):
        ids = [g['representative_id']] + g['collapsed_ids'].split(';')
        mem = [load(byid[i]) for i in ids]
        for d in mem:
            if str(d['id']) in decided:
                d['overall'] = decided[str(d['id'])]
        best = {}
        for d in mem:
            best[d['id']] = max(((jaccard(d['sh'], e['sh']), e['id']) for e in mem if e is not d),
                                key=lambda t: t[0])
        emit(out, 'near_duplicate_ge_0.80', f"DG{g['representative_id']}", mem, best)
        ngroups1 += 1

    # kind 2: exhaustive pairwise check over the candidates
    by_lang = defaultdict(list)
    for i, d in enumerate(cand):
        by_lang[d['lang']].append(i)
    parent = list(range(len(cand)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    best = defaultdict(lambda: (0.0, None))
    npairs = n80 = 0
    for idx in by_lang.values():
        idx = sorted(idx, key=lambda i: len(cand[i]['sh']))
        for pos, i in enumerate(idx):
            si = cand[i]['sh']
            for j in idx[pos + 1:]:
                sj = cand[j]['sh']
                if len(si) < FLOOR * len(sj):
                    break            # sizes only grow from here: Jaccard < FLOOR for the rest
                npairs += 1
                jac = jaccard(si, sj)
                n80 += jac >= THRESHOLD
                if jac >= FLOOR:
                    parent[find(j)] = find(i)
                    for x, y in ((i, j), (j, i)):
                        if jac > best[cand[x]['id']][0]:
                            best[cand[x]['id']] = (jac, cand[y]['id'])
    print(npairs, 'candidate pairs compared exactly;', n80, 'at >= 0.80')
    groups = defaultdict(list)
    for i in range(len(cand)):
        groups[find(i)].append(cand[i])
    ngroups2 = 0
    for g in groups.values():
        if len(g) > 1:
            emit(out, 'similar_0.65_to_0.80', f"ND{min(d['id'] for d in g)}", g, best)
            ngroups2 += 1

    out.sort(key=lambda r: (r['kind'], int(r['group_id'][2:]), r['fmz_id']))
    with open(ROOT / 'near_duplicate_groups.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    k1 = [r for r in out if r['kind'] == 'near_duplicate_ge_0.80']
    k2 = [r for r in out if r['kind'] != 'near_duplicate_ge_0.80']
    print(f'near_duplicate_ge_0.80: {ngroups1} groups, {len(k1)} rows, '
          f'{sum(1 for r in k1 if r["exact_duplicate_of"])} exact duplicates')
    print(f'similar_0.65_to_0.80: {ngroups2} groups, {len(k2)} candidates, '
          f'{sum(1 for r in k2 if r["exact_duplicate_of"])} exact duplicates, '
          f'{len({r["group_id"] for r in k2 if r["members_in_A"] and r["members_in_B"]})} span both halves')


if __name__ == '__main__':
    main()
