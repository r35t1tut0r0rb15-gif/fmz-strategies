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

- `survey_tools/bar_size.py` -> `no_bar_size.csv`: **484 of 5,806 files have no bar size**
  (481 have no backtest header; 3 have a period without a unit: 40155 `15`, 61867 `1440`, and
  one `60`). 85 of the 484 show stop logic (static hint). By language: javascript 289,
  python 100, PineScript 91, MyLanguage 3, cpp 1. By outcome: FLAGGED 202, REJECTED 185,
  PORT_CANDIDATE 70, HELD_NEEDS_VOLUME 15, REJECTED_ON_READING 5, PORTED 5, DUPLICATE 2.
- Correction (same day, second commit): the first version (539 files) only recognised the
  `/*backtest*/` form; MyLanguage writes the header `(*backtest ... *)` and Python
  `'''backtest ... '''`, and one Python file writes `period: 1day`. Fixed; 484 is the count.
- `note` also records any period the code requests (`PERIOD_H1` ...) or the description names;
  these are where the author's own code/words fix the size.

Resume point: Task 3 committed (hash in next entry). Next: Task 4 from id 126968.

Task 3 commits: 0caedb8 (first count, superseded), correction in the next commit.

Task 3 correction commit: f17d01e (pushed, verified).

## Task 4, batch A1 (ids 126968 - 171038)

origin/survey-b did not exist when the batch started (worker B has pushed nothing yet).
Added to SURVEY_README.md: "MyLanguage interpretation rules" (close-price model, function
semantics incl. HV/LV excluding the current bar, AUTOFILTER, BKPRICE, exits as signals).

| id | outcome | note |
|---|---|---|
| 126968 | PORTED | turtle 20/55, daily broker days, donchian_breakout |
| 127101 | PORTED | MACD + dual SMA, 1h, ma_trend |
| 127691 | PORTED | ATR channel stop-and-reverse, 1h; ND127691 |
| 128126 | DUPLICATE_ON_READING of 127691 | same logic and defaults |
| 128249 | PORTED | EMA + KD pullback, 30min |
| 128250 | PORTED | dual EMA + RSI cross, 15min |
| 128418 | PORTED | Kaufman AMA cross, 5min |
| 132298 | PORTED | turtle V1.0, daily |
| 146391 | PORTED | Bollinger band-MA cross, 1min (code's PERIOD_M1) |
| 156699 | PORTED | MA high/low envelope reverse; bar_size_pending |
| 170557 | REJECTED_ON_READING (1) | inventory-ratio ladder on tick prices |
| 170842 | REJECTED_ON_READING (1) | order-API demo, not a strategy |
| 171038 | PORTED | 30min channel vs daily range regime |

All 16 ports pass py_compile and check_ports.py.

Resume point: batch A1 committed (hash in next entry). Next id: 177631.

Batch A1 commit: d85cd82 (pushed, verified).

## Task 4, batch A2 (ids 177631 - 201007)

origin/survey-b still absent at batch start. SURVEY_README: FMZ `TA.Highest/Lowest` read as
excluding the current element (authors' comments; breakout rules need it) - flagged as an
assumption for the project.

| id | outcome | note |
|---|---|---|
| 177631 | REJECTED_ON_READING (1) | inventory-ratio ladder |
| 183416 | PORTED | regression-slope reverse, 1h |
| 186598 | PORTED | spot turtle, daily (code's 24 h records) |
| 187874 | REJECTED_ON_READING (2) | hard-coded BTC price levels |
| 188499 | PORTED | KRT Keltner reverse, daily; source typo `H+L+C)/3` ported as (H+L+C)/3 |
| 188507 | PORTED | typical-price EMA reverse with ATR band gate, daily |
| 191622 | REJECTED_ON_READING (1) | swap order ladder, price-unit offsets |
| 192353 | PORTED | turtle 55/20, author's highest-LOW long exit kept; bar_size_pending |
| 193609 | PORTED | single SMA reverse; bar_size_pending |
| 194224 | PORTED | MACD hist turn, long only; bar_size_pending |
| 200131 | PORTED | log-return range breakout (criterion 2 change of indicator), 15min |
| 200625 | PORTED | SuperTrend flip, 15min |
| 201007 | REJECTED_ON_READING (1) | random (coin-flip) entries |

All 25 ports pass py_compile and check_ports.py.

Resume point: batch A2 committed (hash in next entry). Next id: 205469.
