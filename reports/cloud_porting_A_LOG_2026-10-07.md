# Cloud porting worker A: log (2026-10-07)

Branch `survey`. Worker B works on `survey-b` (ids >= 439378, later downward from 439377); this
worker never touches that branch and checks `origin/survey-b` before every batch.
Static work only: nothing is run, backtested or optimised.

Each entry ends with a **Resume point**. On restart ("continue"): read the last resume point here
and `PROGRESS.md`, and carry on; never redo a pushed batch.

## Task 1: rules 2026-10-07 + check_ports.py

- `SURVEY_README.md`: section "Rules added 2026-10-07" (rules 1-10, marks, checker additions,
  broker-day helper); older text marked superseded where it differs. Rule 5 checked: the contract
  cannot express a Pine `stop=`/`limit=` entry exactly, so only the "as meant" module is ported.
- `check_ports.py`: `Marks:` line; `FREQ = "bar_size_pending"` <-> mark; stop Series built from
  the current bar (no `.shift(k>=1)` inside `stops()`); stop keys; `coarse_bar_stop` on > 1 h;
  resample left/left. Negative-tested on scratch copies (5 cases, all flagged as expected).
- Rule 1 applied to 119038 and also to 11604, 42283, 42451 (same situation: no period in the
  source, old `1h` default). 55839 (author says hourly bars) and 103070 (code requests
  `PERIOD_M15`) keep their source-given sizes.
- All 6 ports pass `py_compile` and `check_ports.py`.

Resume point: Task 1 committed (hash in the next entry). Next: Task 2.

Task 1 commit: cf80b57 (pushed, verified with ls-remote).

## Task 2: duplicates explained + near-duplicate check

- `reports/near_duplicates_2026-10-07.md`: (a) 327 collapsed = 251 DUPLICATE + 61 REJECTED +
  15 FLAGGED (priority order); 7 of the 251 are exact copies, 244 near-duplicates -> rule 7
  decision owed (re-open them?). (b) exhaustive check over 3,747 candidates: 0 pairs >= 0.80,
  124 groups at 0.65-0.80 (302 candidates, 31 groups span both halves).
- `near_duplicate_groups.csv` + `survey_tools/near_dup_candidates.py`.

Resume point: Task 2 committed (hash in next entry). Next: Task 3 (no_bar_size.csv).

Task 2 commit: fc81097 (pushed, verified).

## Task 3: no_bar_size.csv

- `survey_tools/bar_size.py` -> `no_bar_size.csv`: **539 of 5,806 files have no bar size**
  (536 have no `/*backtest*/` header; 3 have a period without a unit: 40155 `15`, 61867 `1440`,
  and one `60`). 94 of the 539 show stop logic (static hint). By language: javascript 289,
  python 131, PineScript 91, MyLanguage 27, cpp 1. By outcome: FLAGGED 219, REJECTED 197,
  PORT_CANDIDATE 91, HELD_NEEDS_VOLUME 19, REJECTED_ON_READING 6, PORTED 5, DUPLICATE 2.
- `note` also records any period the code requests (`PERIOD_H1` ...) or the description names;
  these are where the author's own code/words fix the size.

Resume point: Task 3 committed (hash in next entry). Next: Task 4 from id 126968.
