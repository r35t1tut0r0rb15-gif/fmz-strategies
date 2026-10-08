"""Write reports/cloud_porting_A_report_2026-10-07.md (worker A's final report) from the repo state.

Counts come from ports/, survey_tools/port_manifest.py and git log; the decisions owed are kept
in DECISIONS / AS_WRITTEN below and updated per batch. Static: modules are parsed, never imported.
"""
import ast
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'survey_tools'))
import port_manifest as pm  # noqa: E402

A_START = 126968
B_START = 439378
MARKS = ['bar_size_pending', 'trailing_stop_pending', 'coarse_bar_stop', 'stop_is_entry_condition']

# Ports whose direction or rule is a likely author slip, kept as written (decision owed).
AS_WRITTEN = {
    'direction inverted relative to the source\'s own names or colours': [426848, 
        207157, 361675, 361689, 361996, 362004, 362031, 362172, 362418, 362427, 362649, 362654, 362664,
        362898, 363582, 363590, 365080, 365381, 366941, 366946],
    'formula slip kept': [192353, 345036, 188499, 426854],
    'exit bound to a mis-typed entry id (so one side has no bracket)': [426300],
    'strategy.close naming ids no entry uses (positions end only at the opposite entry)': [426557],
    'bands that look swapped (long test covers most of the range)': [426780],
    'conditions written as bare statements (no effect)': [426816],
    'entry uses the take-profit percent instead of the retrace input': [426843],
    'sell rule reads close > open[1] where the mirror would be close < open[1]': [426885],
    'short threshold +50 where -50 looks meant': [426794],
}

DECISIONS = [
    'Rule 7 re-opening: SURVEY_SUMMARY\'s 251 DUPLICATE rows include only 7 exact copies; the other '
    '244 are near-duplicates that rule 7 would now port. Re-open them as PORT_CANDIDATE or keep them '
    'set aside? (reports/near_duplicates_2026-10-07.md)',
    'Rule 5: the contract cannot express "stop=/limit= as entry condition" (stops() takes only '
    'sl_stop/tp_stop/max_hold_time; entries fill at the next open). The 468 screened files with '
    'strategy.entry(stop=/limit=) were REJECTED at screening; re-open them for the second '
    '("as meant") module only, or extend the contract with entry-price orders?',
    'FMZ TA.Highest/TA.Lowest are read as excluding the current element (ports 171038, 192353, '
    '200131, 271523, 55839); confirm against the FMZ library.',
    'Ports kept as written although the source looks like a slip (see "Kept as written" below): '
    'keep, or add a corrected variant per rule 5-style dual porting?',
    '333269 has no numeric defaults in the source (grid chosen from the argument table only).',
    '200131 and 361827 compute the indicator change as a log return (as the source does).',
    '361719 rejected: request.security resolution "18000" is undefined; the project would have to '
    'define it before it can be ported.',
    '370728 rejected: nested request.security on a Heikin-Ashi ticker (undefined which daily values '
    'reach the orders); same kind of decision as 361719.',
    '426261 rejected: session windows read through time()/security() at 1- and 30-minute '
    'resolutions on an hourly chart (time zone and lower-resolution semantics undefined); same '
    'kind of decision as 361719. 426334 rejected: ta.ema called with 21 lengths at one loop call '
    'site (runtime-defined state). 426478 rejected likewise (375-minute security on daily bars).',
    '426368: an opposite cross issues a reversing entry plus close_all; the port fills them in '
    'issue order (the bar ends flat). If close_all is sized at issue time the reversal would '
    'stand (always-in). Confirm the broker-emulator reading.',
    'Multi-day header periods: 426502 / 426561 (3d), 426581 (2d), 426604 (4d) are built from broker '
    'days in fixed blocks of broker-day dates counted from 1970-01-01, 426516 (7d) from calendar '
    'weeks of broker-day dates. Confirm the block phase.',
    '426561 has a bare word "Stochastic" on line 129 (does not compile as written); ported reading '
    'it as a lost comment.',
    'Session / weekday / hour rules on crypto pairs are read in UTC (426511, 426779; TradingView\'s '
    'Binance time zone); FMZ\'s exchange time zone is not documented.',
    '426625 passes qty = 0 on every entry (read literally, no order is sized); the signal rule is '
    'ported. Confirm, or reject as no-trade.',
    '426778 calls ta.atr inside if-blocks; the port follows TradingView\'s per-call-site history '
    '(each ATR advances only on its own bars). FMZ\'s runtime may differ.',
    'Data-start dependence also in 426619 (AMA from nz 0) and 426626 (previous-year high / low, '
    'partial first year).',
    '426483 (unit strategy.order on alternating crosses) holds +1 / 0 or -1 / 0 depending on the '
    'first cross in the data: data-start dependence as 366388 / 370711.',
    'Account-currency P/L exits and equity protectors (426842, 426847) are treated as balance '
    'checks (sizing, README) and not ported; 426556 was rejected mainly for its averaging ladder. '
    'Confirm.',
    '426825 rejected because its entry reads its own moving stop; it can be ported once moving '
    '(trailing) stops are expressible.',
    'Same-bar entry and exit: ports from batch A23 on resolve them in Pine\'s order inside '
    'simulate(); earlier long-only ports that return raw le / lx leave a same-bar conflict to the '
    'engine. Audit owed.',
    'Correction (A27): 426461, 426509 and 426588 had been rejected as pyramided ladders, but '
    'SURVEY_README classes pyramiding adds as sizing; they are now ported (net position). '
    'Ladders whose exits read the averaged price or unit counts stay rejected (426570, 426882). '
    'The earlier martingale / averaging rejections (395966, 416875, 422794) may likewise be '
    'portable as a net position under that rule; re-read owed.',
    '426856: a limit exit at the bar\'s close is ported as a close-based exit at the next open.',
    'strategy.exit with no price arguments is read as "no exit" (426361 rejected, 426455 '
    'rejected for re-issued exit ids).',
    '362214 is one-sided as written (the source never opens the other side).',
    '55839 keeps FREQ "1h" (author states hourly bars in the text); 103070 keeps PERIOD_M15 from '
    'the code. Bar sizes requested in code (GetRecords(PERIOD_xx)) are treated as the source\'s '
    'bar size, not as a choice.',
    'FAMILY values are proposals ("user to confirm") in every port.',
    'Sources whose orders are degenerate were rejected on reading (criterion 1): 368717 (long entries, '
    'no exit at all), 368734 and 369999 (a count / plot handle tested as a boolean, so long on almost '
    'every bar). Confirm that "no testable rule" is a valid rejection, or port them as written.',
    'Some ports depend on where the data starts (Pine cum() / bar_index running means: 366388 cancels '
    'it, 370711 does not); acceptable?',
]


def docstring(path):
    return ast.get_docstring(ast.parse(path.read_text(encoding='utf-8'))) or ''


def marks(path):
    m = re.search(r'^\s*Marks:\s*(.+)$', docstring(path), re.M)
    vals = {v.strip() for v in m.group(1).split(',')} if m else set()
    return vals - {'none'}


def main():
    ports = {}
    for d in sorted((ROOT / 'ports').iterdir()):
        if (d / 'module.py').exists():
            ports[int(d.name.split('_')[0])] = d
    a_ports = sorted(i for i in ports if A_START <= i < B_START)
    a_rej = {i: v for i, v in pm.REJECTED_ON_READING.items() if A_START <= i < B_START}
    a_dup = {i: v for i, v in pm.DUPLICATE_ON_READING.items() if A_START <= i < B_START}
    rej_tally = Counter(f'criterion {c}' for c, _ in a_rej.values())
    mark_count = Counter()
    for i in a_ports:
        mark_count.update(marks(ports[i] / 'module.py'))
    upgraded = [i for i in (11604, 42283, 42451, 119038) if i in ports]
    up_marks = Counter()
    for i in upgraded:
        up_marks.update(marks(ports[i] / 'module.py'))
    stops = [i for i in a_ports if 'USES_STOPS = True' in (ports[i] / 'module.py').read_text()]
    last_id = max(a_ports + list(a_rej) + list(a_dup))
    log = subprocess.run(['git', 'log', '--format=%h %s', '--grep=^survey A'], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip().splitlines()
    nxt = re.search(r'Next id: (\d+)', (ROOT / 'PROGRESS.md').read_text())

    out = ['# Cloud worker A: FMZ porting report (2026-10-07)', '',
           'Branch `survey`. Rules of 2026-10-07 (SURVEY_README.md). Static work only: nothing was run, '
           'backtested or optimised. Per-batch detail and resume points: '
           '`reports/cloud_porting_A_LOG_2026-10-07.md`.', '',
           '## Counts (worker A, ids 126968 and up)', '',
           f'- Ported: **{len(a_ports)}** ({len(stops)} with stops(): {", ".join(map(str, stops)) or "-"})',
           f'- Rejected on reading: **{len(a_rej)}** '
           f'({", ".join(f"{k}: {v}" for k, v in sorted(rej_tally.items()))})',
           f'- Exact duplicate on reading (set aside, rule 7): **{len(a_dup)}** '
           f'({", ".join(f"{i} of {v[0]}" for i, v in a_dup.items())})',
           f'- Last id reached: **{last_id}**; next id in the queue: **{nxt.group(1) if nxt else "?"}**',
           '- Existing batch-1 ports re-marked under rule 1 (logic unchanged): '
           f'{", ".join(map(str, upgraded))} ({", ".join(f"{k} {v}" for k, v in sorted(up_marks.items()))})',
           '', '### Marks on worker A ports', '', '| Mark | Ports |', '|---|---|']
    for m in MARKS:
        out.append(f'| {m} | {mark_count.get(m, 0)} |')
    out += ['', '### Rejections (criterion, id, reason)', '']
    for i, (c, why) in sorted(a_rej.items()):
        out.append(f'- {i} (criterion {c}): {why}')
    out += ['', '### Commits (newest first)', '']
    out += [f'- `{line}`' for line in log]
    out += ['', '## Kept as written', '']
    for k, ids in AS_WRITTEN.items():
        out.append(f'- {k}: {", ".join(map(str, sorted(ids)))}')
    out += ['', '## For the project chat', '',
            '**Finished**', '',
            '- Task 1: rules 2026-10-07 in SURVEY_README.md; check_ports.py extended (Marks line, '
            'bar_size_pending only with its mark, stop Series shifted inside stops(), coarse_bar_stop, '
            'left-labelled resampling); all ports pass.',
            '- Task 2: DUPLICATE 251 explained (reports/near_duplicates_2026-10-07.md); '
            'near_duplicate_groups.csv over all 3,747 PORT_CANDIDATE rows (5-token shingles, exact '
            'Jaccard; >= 0.80 none new, 0.65-0.80 band grouped as ND).',
            '- Task 3: no_bar_size.csv: 484 of 5,806 files have no bar size (85 with stop logic).',
            f'- Task 4: {len(a_ports)} ported, {len(a_rej)} rejected, {len(a_dup)} duplicate on reading, '
            f'ids {A_START} to {last_id}.',
            '', '**Failed / not done**', '',
            f'- Task 4 is not complete: the queue continues at {nxt.group(1) if nxt else "?"}; worker B\'s '
            'branch `survey-b` did not exist on origin at any batch start, so the stop condition was '
            'never reached.',
            '- Rule 5 module (1) ("exactly as written") cannot be expressed by the contract; no '
            'stop_is_entry_condition port exists.',
            '', '**Decisions owed**', '']
    out += [f'{n}. {d}' for n, d in enumerate(DECISIONS, 1)]
    path = ROOT / 'reports' / 'cloud_porting_A_report_2026-10-07.md'
    path.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print('wrote', path.relative_to(ROOT))


if __name__ == '__main__':
    main()
