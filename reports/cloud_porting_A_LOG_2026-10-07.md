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

Batch A2 commit: f63a58e (pushed, verified).

## Task 4, batch A3 (ids 205469 - 345036)

origin/survey-b still absent at batch start.

| id | outcome | note |
|---|---|---|
| 205469 | REJECTED_ON_READING (1) | one-direction accumulation ladder |
| 207157 | PORTED | RSI2 vs SMA as written (inverse of Connors' rule; flagged), 15min |
| 224799 | PORTED | Parabolic SAR side (TA-Lib SAR), 1h (code's 3600 s) |
| 255502 | REJECTED_ON_READING (1) | two concurrent hedged sub-systems with scale ladders |
| 262467 | PORTED | TD count fade, 1h |
| 266142 | REJECTED_ON_READING (1) | pure 50/50 rebalancing |
| 271523 | PORTED | weekly breakout/MA regime, long only, daily |
| 288889 | PORTED | RSI 30/70 long only, 4h |
| 299799 | REJECTED_ON_READING (2) | AHR999 Bitcoin-only model, DCA |
| 301620 | PORTED | EMA cross + MACD confirm, close stop/target, 1h |
| 318486 | PORTED | MA20 entry / MA10 exit, 5min |
| 333269 | PORTED | dual-EMA turning points, no numeric defaults in source (declared), 1h |
| 345036 | PORTED | ATR-active RSI swing long (author's divisor slip kept), 15min |

All 34 ports pass py_compile and check_ports.py.

Resume point: batch A3 committed (hash in next entry). Next id: 345289 (last bot before the
PineScript block, which starts at 356844).

Batch A3 commit: e7ceef7 (pushed, verified).

## Task 4, batch A4 (ids 345289 - 361689)

origin/survey-b still absent at batch start. SURVEY_README: "PineScript interpretation rules"
added before the first Pine port (timing, entries/reversal, exits -> stops()/signals/marks,
ta.* semantics, backtest windows, request.security, inputs).

| id | outcome | note |
|---|---|---|
| 345289 | PORTED | MA order + RSI dip, long only, 15min (last JS bot) |
| 356844 | PORTED | MACD signal cross reverse, daily |
| 359806 | PORTED | SuperTrend with slope filter, daily |
| 360536 | PORTED | Pine turtle 20/55/10, daily |
| 361360 | PORTED | hourly vs daily EMA side, on 1h bars, signals at the 17:00 NY close |
| 361508 | PORTED | squeeze-momentum histogram turns, daily |
| 361521 | PORTED | WaveTrend extremes, 1h |
| 361532 | PORTED | MACD gap side (90 USD -> ATR), 1h |
| 361554 | PORTED | DI+/DI- side, daily |
| 361565 | PORTED | pivot flags with market orders (no stop= in this copy), 12h |
| 361567 | PORTED | OTT VAR cross (percent -> ATR), 1h; ND361567 with 433011 |
| 361675 | PORTED | sling-shot signals faded as written, 15min |
| 361689 | PORTED | three-line strike faded as written, 4h |

All 47 ports pass py_compile and check_ports.py.

Resume point: batch A4 committed (hash in next entry). Next id: 361718.

Batch A4 commit: f98a858 (pushed, verified).

## Task 4, batch A5 (ids 361718 - 361847)

origin/survey-b still absent at batch start.

| id | outcome | note |
|---|---|---|
| 361718 | PORTED | swing pivot side (long on swing high, as written), 2h |
| 361719 | REJECTED_ON_READING (1) | HTF resolution '18000' undefined (would mean choosing a bar size) |
| 361725 | PORTED | low-pass filter cross, 1h |
| 361783 | PORTED | engulfing reverse, 1h (declared min-body variants; 0 = source) |
| 361785 | PORTED | K's reversal (band + MACD cross), 30min |
| 361786 | PORTED | HMA turn + McGinley filter, sl_stop initial; marks bar_size_pending, trailing_stop_pending |
| 361794 | PORTED | JMA ATR envelope reversion, 1h |
| 361802 | PORTED | pivot confirm side, 1h |
| 361827 | PORTED | Pine version of 200131 (log return), daily |
| 361834 | PORTED | H/L z-score reversion, 1h |
| 361839 | PORTED | MACD 12/26/9 cross on 1h (near #356844, not exact) |
| 361844 | PORTED | JMA vs DWMA cross with pivot exits, 1h |
| 361847 | PORTED | TD setup 13 fade; bar_size_pending |

All 59 ports pass py_compile and check_ports.py.

Resume point: batch A5 committed (hash in next entry). Next id: 361880.

Batch A5 commit: 2ef3770 (pushed, verified).

## Task 4, batch A6 (ids 361880 - 362092)

origin/survey-b still absent at batch start. 13 ported, 0 rejected:
361880 triple SuperTrend (2h); 361969 QQE+SSL+WAE confluence (4h, swing sl_stop, coarse_bar_stop;
simulate mirrors the engine stop for flat-state gating); 361974 smoothed %R turns (4h);
361977 T3 cloud oscillator (2h); 361996 HA bias faded as written (10min); 362000 HA EMA trend (4h);
362004 envelope cross faded as written (4h, percent -> ATR); 362031 Chande-Kroll cross faded as
written (bar_size_pending); 362055 Big Snapper state machine (2h); 362059 SMA trend + BB cross
(15min, trailing_stop_pending); 362060 MACD cross divergence (4h); 362089 EMA/SMA cross + MACD
(15min); 362092 EMA 20/200 cross (4h).

All ports pass py_compile and check_ports.py.

Resume point: batch A6 committed (hash in next entry). Next id: 362103.

Batch A6 commit: 7617e69 (pushed, verified).

## Task 4, batch A7 (ids 362103 - 362418)

origin/survey-b still absent at batch start. 13 ported, 0 rejected:
362103 EHMA band reverse (daily, % -> ATR); 362163 normalised momentum cross (30min);
362167 EMA/Aroon/ASH with fixed SL/TP via stops() (3min; simulate mirrors the engine stop/target);
362168 MTF RSI/Stoch average (1h bars, daily decisions; W/D/4h/1h); 362172 fast stoch faded (1h);
362178 PSAR regression band flip (15min; TradingView pine_sar); 362210 SSL hybrid continuation (30min);
362214 AMACD deal state (one-sided as written, 30min); 362223 HL2/Kijun cross (bar_size_pending);
362256 Follow Line flip (15min); 362327 HMA local-extreme cross (5min); 362403 BB/RSI/ADX (1h);
362418 Williams fractal side (1h).

All ports pass py_compile and check_ports.py.

Resume point: batch A7 committed (hash in next entry). Next id: 362427.

Batch A7 commit: 0b7843c (pushed, verified).

## Task 4, batch A8 (ids 362427 - 362664)

origin/survey-b still absent at batch start. 13 ported, 0 rejected:
362427 EMA/Kijun cross faded as written (bar_size_pending); 362430 MACD histogram cross with EMA
50/200 trend (30min); 362443 EMA 20/50 side (4h); 362457 triple SuperTrend agreement (30min);
362497 MAHL band (10min); 362499 EMA/SMA cross + return sign + daily SuperTrend (1h);
362542 confirmed pivots (bar_size_pending); 362572 3-EMA pullback zone (5min); 362637 ESSMA vs
its WMA (1h); 362638 2/20 EMA + bandpass combo (bar_size_pending, zones -> ATR); 362649 rolling
Heikin Ashi faded as written (6h); 362654 RSI+BB extreme faded as written (10min); 362664 RSI
divergence faded as written (10min).

All ports pass py_compile and check_ports.py.

Resume point: batch A8 committed (hash in next entry). Next id: 362667.

Batch A8 commit: f252a14 (pushed, verified). Interim final report: 8f62b3b
(`survey_tools/report_a.py` regenerates `reports/cloud_porting_A_report_2026-10-07.md`).

## Task 4, batch A9 (ids 362667 - 363579)

origin/survey-b still absent at batch start. 11 ported, 2 rejected:
362667 HalfTrend + HEMA + SMA (5min); 362671 Moon Launch state machine (5min, DG362671);
362842 SSS SSL flip long-only with 1 % tp_stop and close-based exit (15min, DG362842);
362868 Mobo bands (1h); 362870 BRAHMASTRA Kalman HMA cross (2h); 362887 range filter + UO + EMA
(2h); 362898 RSI extreme cross, overbought -> long as written (5min); 363001 CMO cross + momentum
+ SuperTrend, equity-curve sizing stored (15min, DG363001); 363002 Rainbow oscillator (1h);
363562 Sidboss range filter (30min); 363579 Smarter MACD rising bottoms (3min).
Rejected (criterion 1, request.security lookahead_on without [1] reads the future): 363557, 363572.

Fix found while checking: 15 earlier ports (A5-A8) did not name their near-duplicate group in
PORT_NOTES.md row 6 (rule 7). All fixed; check_ports.py now flags it (negative-tested).

All ports pass py_compile and check_ports.py.

Resume point: batch A9 committed (hash in next entry). Next id: 363582.

Batch A9 commit: a9d6425 (pushed, verified).

## Task 4, batch A10 (ids 363582 - 363847)

origin/survey-b still absent at batch start. 13 ported, 0 rejected:
363582 CCI on 5 lower timeframes, overbought -> long as written (15min bars, 12h decisions);
363588 Octa-EMA + Ichimoku (10min, DG363588); 363590 RSI on 5 timeframes, overbought -> long as
written (15min); 363749 LuxAlgo Fibonacci progression (5min); 363766 SMA/ADX/KAMA + pivot ATR
trend close_all (2h); 363793 Trendelicious (30min); 363797 EMA cross with close-based trail and
3.5 % close stop (1h, trailing_stop_pending, ND363797); 363803 Super Scalper (1min);
363807 slow SuperTrend (1min); 363824 QQE momentum zigzag (10min); 363825 SuperTrend on close
(1min); 363829 Pivot Point SuperTrend (1min); 363847 RISOTTO RSI/OTT (1min).
New scratch helpers: higher/lower-timeframe blocks from the port's bars with an as-of read of
completed blocks (searchsorted, no fill).

All ports pass py_compile and check_ports.py.

Resume point: batch A10 committed (hash in next entry). Next id: 363848.

Batch A10 commit: 344c9f9 (pushed, verified).

## Task 4, batch A11 (ids 363848 - 365075)

origin/survey-b still absent at batch start. 13 ported, 0 rejected:
363848 Chandelier Exit flips (30min); 363980 RSI(open) regular divergence (10min);
363997 Bollinger turn-back on opens (30min); 364001 RedK momentum bars (3min); 364037 EMA 9/20
cross (30min); 364518 AO+Stoch+RSI with ATR stop/target via stops() (30min, trailing_stop_pending:
levels re-set on repeated signals; DG364518); 364527 Heikin-Ashi PAC pull-back (3min);
364535 SMA 8/20 cross (bar_size_pending); 364536 HODL line (5min); 364540 CM MACD zero-side
cross (10min, ND364540); 365028 QQE signals (10min, DG365028 + ND365028); 365059 fractal box
(45min, no parameters: 1 trial); 365075 order-block sequence (30min).
Scratch fix: the group writer now names every group of an id (365028 is in two).

All ports pass py_compile and check_ports.py.

Resume point: batch A11 committed (hash in next entry). Next id: 365078.

Batch A11 commit: 70754b7 (pushed, verified).

## Task 4, batch A12 (ids 365078 - 365389)

origin/survey-b still absent at batch start. 12 ported, 1 rejected:
365078 ATR trailing-stop flips (2h); 365080 red-bar RSI(open) extreme, higher RSI -> long as
written (10min); 365127 Trading ABC zigzag pull-back (30min); 365128 SuperTrend around EMA 100
(10min); 365283 MACD on VAR averages (30min, DG365283); 365314 EMA 50/100 cross with close
confirmation (15min); 365315 QQE fast/slow cross (1h); 365320 consolidation-zone breakout
(45min); 365345 linear-regression channel reversion (45min); 365359 RSI divergence Libertus
(bar_size_pending); 365373 Super Scalper RSI-pair (5min, DG365373); 365381 Matrix Series,
overbought -> long as written (15min).
Rejected: 365389 (criterion 1: 50 % partial take-profit ladder in ticks; criterion 2 too).

All ports pass py_compile and check_ports.py.

Resume point: batch A12 committed (hash in next entry). Next id: 365419.

Batch A12 commit: a625008 (pushed, verified).

## Task 4, batch A13 (ids 365419 - 365727)

origin/survey-b still absent at batch start. 13 ported, 0 rejected:
365419 Bollinger basis cross + AO (1h); 365600 engulfing + SMA with TP/SL 2000/200 USD -> ATR
multiples via stops() and a close-based MA exit (30min, DG365600); 365642 PAC break with EMA 180
filter (2h); 365668 Hull swing / EMA pull-back with RSI closes and a 750-tick stop -> ATR multiple
(30min, DG365668); 365671 ChartArt Stoch + RSI (30min, DG365671); 365691 PMax (15min, DG365691 +
ND365691); 365695 broken fractal (1h, 1 trial); 365706 SMA cross follow-through (4h);
365711 zigzag harmonic patterns with high/low-checked closes (1h, ND365711); 365713 NRTR (2h);
365719 LuxAlgo pivots (daily broker days); 365722 PSAR flips (15min); 365727 Hull Suite (30min,
DG365727 + ND365727).

All ports pass py_compile and check_ports.py.

Resume point: batch A13 committed (hash in next entry). Next id: 365858.

Batch A13 commit: a0358a3 (pushed, verified).

## Task 4, batch A14 (ids 365858 - 366430) (worker restarted mid-batch; resumed from the
uncommitted files, nothing redone)

origin/survey-b still absent at batch start. 13 ported, 0 rejected:
365858 SSL channel 2 flips (45min, ND365858); 365859 range filter (10min, DG365859);
365892 dual SuperTrend + ROC with fixed 5 % / 6 % sl_stop (10min, DG365892); 365898 EMA/RSI/ADX
scalper (5min); 365905 Schaff trend cycle (45min); 365907 EMA/SMA swing cross (1min);
366385 linear-regression band cross (4h); 366388 Bollinger lows swing line (4h); 366389 SMA swing
trend, log(10) price offset -> ATR (4h); 366391 RSI extrapolated extremes (4h); 366404 regression
peak detector (4h); 366407 SuperTREX (4h); 366430 MACD cross divergence (4h, DG366430).
Authors: Zer3192 from 366385 on.

All ports pass py_compile and check_ports.py.

Resume point: batch A14 committed (hash in next entry). Next id: 366641.

Batch A14 commit: 8d1813b (pushed, verified).

## Task 4, batch A15 (ids 366641 - 367572)

origin/survey-b still absent at batch start. 13 ported, 0 rejected:
366641 Delta-RSI polynomial slope (1h); 366930 SAMA slope colour (10min); 366936 pivot distance
trend (30min); 366941 RSI divergence, bearish -> long as written (5min, ND366941); 366942 PSAR
classic flips (5min); 366943 MACD Bollinger break (45min); 366946 BB + stoch-RSI extreme, Bear ->
long as written (15min); 366947 Demark setup (30min); 366948 Darvas box (45min); 366966 Fibonacci
timing pattern (4h, 1 trial); 367476 regression channel trend (4h, ND362178); 367565 swing stop
line (4h); 367572 SAR envelope cross (4h).

All ports pass py_compile and check_ports.py.

Resume point: batch A15 committed (hash in next entry). Next id: 367643.
