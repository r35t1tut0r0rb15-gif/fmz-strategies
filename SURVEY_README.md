# FMZ survey and conversion (branch `survey`)

Session 5E-cloud, started 2026-09-29, from `master` at commit 7853bb2 (the raw FMZ corpus:
5,806 strategy files plus `README.md`). The original corpus files at the repository root are
never modified, moved or deleted. Everything this work adds lives in the paths listed below.

**Hard rules.** Nothing here is backtested, run or ranked. Ports are converted only; the desktop
runs admission checks later. FMZ's own performance claims (descriptions, "annualised N%" in
names, backtest screenshots) are ignored and never used in any decision (criterion 7).

## Admission criteria (fixed before any survey result was read)

1. Fits the strategy interface: signals are acted on at the next bar's open, and never use the
   prices of the bar they signal on.
2. Generic across instruments: volatility-normalised parameters, no hard-coded price levels.
3. Needs crypto-exchange-only features (funding rates, order book, perpetual-swap mechanics) ->
   FLAG AND STORE the original, do not convert it to run. Kept for future crypto-exchange work.
4. The port carries signals only. The original sizing and money-management code is stored
   verbatim beside each port, labelled, for later testing as a separate layer.
5. Each port's parameter ranges are declared before any backtest. A coarse grid first,
   narrowing later on training data only. Every point counts as a trial. A strategy with no
   parameters gets a few declared starting variants.
6. Near-duplicates are collapsed to one representative, and the others are listed. *(2026-10-07: near-duplicates are now ported too, exact duplicates set aside; rule 7.)*
7. FMZ's own performance claims are ignored.

## Layout

| Path | What |
|---|---|
| `SURVEY_README.md` | this file: method, contract, interpretation rules |
| `SURVEY_SUMMARY.md` | counts per criterion outcome; every flagged/stored item with its reason |
| `PROGRESS.md` | what is screened, ported and next; any later session resumes from it |
| `screening.csv` | one row per corpus file: preliminary outcome of criteria 1, 2, 3, 6 with reasons |
| `review_decisions.csv` | final outcomes decided by reading a file (overrides `screening.csv`) |
| `duplicates.csv` | criterion 6: representative id -> collapsed ids |
| `possible_duplicates.csv` | pairs just under the collapse threshold, checked by hand before porting |
| `near_duplicate_groups.csv` | 2026-10-07: screen groups (`DG<rep>`, >= 0.80, all members) and exhaustive 0.65-0.80 groups among the remaining candidates (`ND<id>`); method in `survey_tools/near_dup_candidates.py` |
| `no_bar_size.csv` | 2026-10-07: every corpus file with no bar size (rule 1), language, stop logic flag |
| `reports/` | 2026-10-07: worker logs and reports |
| `ports/<fmz_id>_<slug>/module.py` | the port |
| `ports/<fmz_id>_<slug>/original_source.md` | verbatim copy of the FMZ file |
| `ports/<fmz_id>_<slug>/original_sizing.txt` | verbatim sizing / money-management code with line references (criterion 4) |
| `ports/<fmz_id>_<slug>/PORT_NOTES.md` | outcome of each of the 7 criteria, declared GRID and why, ambiguities resolved |
| `flagged/<fmz_id>_<slug>/` | criterion 3: `original_source.md` (verbatim) + `REASON.md`; not ported |
| `survey_tools/` | the static screening scripts (read text only; never execute strategies) |

Line references in `original_sizing.txt` are line numbers in `original_source.md`.

## Rules added 2026-10-07 (they win over everything below and over `PROGRESS.md`)

Given by the project on 2026-10-07. Where they differ from older text in this file, these win;
the older text is left in place for the record and marked "superseded 2026-10-07".

1. **No bar size in the source** (no `/*backtest*/ period`, or a period without a unit, e.g.
   ids 61867 `period: 1440` and 40155 `period: 15`): set `FREQ = "bar_size_pending"` exactly and
   add the mark `bar_size_pending`. Never choose a bar size. This replaces the old `FREQ = "1h"`
   default. Applied to the existing ports 119038, 11604, 42283 and 42451 (all four had used the
   `1h` default), logic unchanged. Such a module cannot run until the project sets `FREQ`
   (`precompute` raises on the unknown frequency). A bar size the code itself requests
   (e.g. `GetRecords(PERIOD_M15)`) or the author states in so many words is the source's own.
2. **Trailing stop**: port the strategy and mark it `trailing_stop_pending`. `stops()` has no
   trailing key, so the trailing stop is described exactly in `PORT_NOTES.md` (distance as an
   ATR multiple, activation) and quoted in `original_sizing.txt`, and is not emitted until the
   project decides how to express it. An author's trail checked on closes is ported as a
   close-based exit signal from `simulate()`, not as a stop (no mark needed).
3. **Pine close-based stop** (`if close < stopLevel` -> `strategy.close`): always a close-based
   exit signal from `simulate()`, never `sl_stop`.
4. **Stops on bars longer than 1 h**: port normally and mark `coarse_bar_stop`.
5. **Pine `strategy.entry(..., stop=, limit=)`**: port TWO modules: (1) exactly as written,
   marked `stop_is_entry_condition`; (2) as the author evidently meant (a real stop-loss and
   take-profit at those levels), under its own name, the assumption stated in its notes. First
   check that the contract can express (1); if it cannot, report it and port only (2), marked.
   *Checked 2026-10-07 (worker A):* the contract cannot express (1). A Pine `stop=`/`limit=` entry
   is a resting order that fills inside a bar at its own price; the contract has only boolean
   signals filled at the next bar's open. Re-reading the level as "enter next open once a
   completed bar crossed it" changes both the trigger and the fill, so it is not "exactly as
   written". Hence only (2) is ported, marked `stop_is_entry_condition`, and the case is reported.
   Note: the static screen already sent every such file (468) to `REJECTED`
   ("entries are resting limit/stop orders ..."), so none is in the `PORT_CANDIDATE` queue; whether
   to re-open them under this rule is a project decision.
6. **Reversals**: declare `REVERSAL INTENDED` in the docstring, or return
   `upon_opposite_entry="ignore"` from `portfolio_kwargs` when the source only enters when flat.
   Do NOT create long-only / short-only split versions. (A source that is itself long-only, e.g. a
   spot bot, is ported as it is and says "Long only".) `{"upon_opposite_entry": "ignore"}` is
   allowed in `portfolio_kwargs` of a stop-using port too; that is the only key it may hold there.
7. **Near-duplicates are still ported**, each with its group id from `near_duplicate_groups.csv`
   in `PORT_NOTES.md`. Exact duplicates stay set aside. (Supersedes criterion 6's "collapsed to one
   representative" for ports made from 2026-10-07 on.)
8. `HELD_NEEDS_VOLUME` and `FLAGGED_CRYPTO_ONLY` rows are not ported.
9. A real module never contains the text `KNOWN_ANSWER_TEST` anywhere, not even in a comment.
   Daily bars are broker days (17:00 New York), never `resample("1D")`; intraday bars resample with
   `label="left", closed="left"`, no ffill. No whole-series statistics, centred windows, bfill or
   `shift(-k)`. No costs in a module.
10. **Static checks only**: `py_compile` and `survey_tools/check_ports.py` on every port. Never
    run, backtest or optimise anything.

**Marks.** Every module's docstring ends with one line `Marks: none` or `Marks: a, b`, using only
`bar_size_pending`, `trailing_stop_pending`, `coarse_bar_stop`, `stop_is_entry_condition`.
`PORT_NOTES.md` repeats them under "Marks".

**check_ports.py additions (2026-10-07).** It also flags: a missing or unknown `Marks:` line;
`FREQ = "bar_size_pending"` without the mark (or the mark without that FREQ); a `stops()` that
reads its bars argument but has no `.shift(k)` (k >= 1) inside `stops()` itself, i.e. a stop
Series built from the current bar; `stops()` keys other than `sl_stop`/`tp_stop`/`max_hold_time`;
stops on a FREQ longer than 1 h without `coarse_bar_stop`; any `resample()` that is not
`label="left", closed="left"`.

**Broker days in a module.** A daily port defines `broker_day(index)` locally (session ends 17:00
America/New_York; the desktop binds the name to `registry_schema.broker_day`) and groups 1-minute
bars by it; each daily bar is stamped with its session's UTC start.

## Strategy interface (the project's execution contract)

Python, vectorbtpro. Each port is ONE module exposing exactly:

```
NAME: str
FAMILY: str                            # strategy family = trial-deflation group; a run spec naming a
                                       # different family is refused by the mining driver
GRID: dict[str, list]                  # declared parameter ranges (criterion 5)
DEFAULT_PARAMS: dict                   # superset of GRID's keys
FREQ: str                              # vbt frequency of the module's bars, e.g. "1h"
PERIODS_PER_YEAR_OVERRIDE: int | None  # usually None
precompute(raw_1m_df, symbol_key, **params) -> bars_df
    open/high/low/close, tz-aware UTC index, strictly increasing.
    Resample 1-minute bars with label="left", closed="left". Never forward-fill.
simulate(bars_df, **params) -> (long_entries, long_exits, short_entries, short_exits)
    four BOOLEAN Series on exactly bars_df.index
portfolio_kwargs(**params) -> dict     # normally {}. Never price=, open=, fees, slippage or swap.
```

Stop-using ports also set `USES_STOPS = True` and define `stops(bars, **params)` returning a dict
with only `sl_stop`, `tp_stop`, `max_hold_time` (fractions of the entry fill price);
`portfolio_kwargs` must then be empty. *(2026-10-07: except `{"upon_opposite_entry": "ignore"}`, rule 6.)*

The name `KNOWN_ANSWER_TEST` must not appear anywhere in a port module, not even in a comment.

*Added 2026-10-03 (fix pass): `FAMILY` and the `KNOWN_ANSWER_TEST` rule come from the house
strategy-authoring contract; the 2026-09-29 interface summary had left them out.*

Timing rules: a signal is True on the bar whose data generates it; the engine lags every signal
one bar and fills at that bar's open. Ports never shift signals and never use `shift(-k)`. No
whole-series statistics, centred windows or bfill. Rolling windows end at the current bar, and
each port says whether the current bar is included. Higher-timeframe values are used only after
the higher bar closes. Daily bars are broker days (end 17:00 America/New_York) via
`broker_day(index)`, bound by the desktop to `registry_schema.broker_day`. Pine's
`strategy.entry` reverses by default, so each port declares either
`{"upon_opposite_entry": "ignore"}` or "reversal intended" in its docstring. No cost constants.

**Prefer flat before reverse.** Swap (overnight financing) is booked on the first flat bar, so a
port should close a position and open the opposite one on a later bar, not reverse in one bar,
unless the strategy's logic requires the one-bar reversal. A port that reverses in one bar says so.
The three batch-1 ports that reverse in one bar (11604, 55839, 119038) are left as written; their
flat-first variants are pending a project decision (see `PROGRESS.md`).

**Time exits for FTMO strategies with shorts** are explicit exit signals emitted by `simulate()`,
not `max_hold_time` in `stops()`.

## Interpretation rules applied to every port

These are fixed here, before porting, so they are applied the same way to every file.

- **Missing bars.** `precompute` drops resample periods that contain no 1-minute bar (all four
  prices NaN). Nothing is forward-filled or synthesised.
- **Criterion 1: what fits.** The test is: can the decision rule be evaluated once per completed
  bar, from data up to and including that bar, without changing the rule itself?
  - Rules written on bar fields or indicators (`close > band`, MA slope, RSI cross) fit. FMZ bots
    that poll the forming bar (`records[len-1]`) are ported as the same rule evaluated on the
    completed bar; the port notes say so.
  - Rules that need a fill at a price reached inside the bar do not fit: Pine entries with
    `limit=`/`stop=` prices, `process_orders_on_close`, `calc_on_every_tick`,
    `calc_on_order_fills`, and bots whose entries trigger on tick prices crossing levels or on
    tick-tracked highs/lows (e.g. R-Breaker style intraday level breaks, tick state machines).
  - FMZ bots reading `records[len-2]` (the last completed bar) map exactly: signal on that bar.
- **Criterion 2: price units.** Distances in price units, ticks, points or percent are
  re-expressed as multiples of ATR (Wilder, length declared), so the port is volatility
  normalised. Absolute price levels (e.g. `close > 25000`), named external instruments and
  ticker-specific branches fail criterion 2. Oscillator thresholds (RSI 30/70 etc.) and bar
  counts are already dimensionless and stay as they are.
- **Criterion 4: what counts as sizing / money management.** Stored verbatim, not ported:
  order quantities, % of equity, leverage, pyramiding, martingale/averaging-in, balance checks,
  minimum-trade guards, slippage/price offsets, and trailing stops that `stops()` cannot express.
  *(2026-10-07: trailing stops are now ported with the mark `trailing_stop_pending`; rule 2.)*
  Fixed stop-loss / take-profit exits that `stops()` can express are ported there *and*
  quoted in `original_sizing.txt`, so the separate layer can also test them. A trailing exit
  that the original evaluates on bar closes as its only exit is part of the signal and is ported
  as a signal exit. Time exits are explicit exit signals from `simulate()` (required for FTMO
  strategies with shorts; see "Time exits" above), and the original time-exit code is quoted too.
- **Stops as Series.** The engine lags the four signal Series one bar, but it passes `sl_stop` /
  `tp_stop` Series to vbt UNLAGGED, and vbt reads them on the entry FILL bar (signal bar + 1).
  So a per-bar stop must use bars up to the previous bar only, e.g. `(k * atr / close).shift(1)`:
  the value read on the fill bar then comes from the signal bar. (Corrected 2026-10-03; the
  2026-09-29 text assumed the engine lagged stops like signals. No batch-1 port returns a stop
  Series, so no port changed.)
- **Volume.** The contract's bars carry open/high/low/close only, and CFD volume is broker tick
  volume anyway. Strategies whose signals use volume are held (`HELD_NEEDS_VOLUME`) until the
  project confirms whether volume is available and meaningful.
- **Bar size.** `FREQ` is the original's backtest period when the source declares one (FMZ's
  `backtest ... period:` header). When it does not, the port uses `1h` and says so.
  *Superseded 2026-10-07 by rule 1: `FREQ = "bar_size_pending"` + mark, never a chosen size.*
- **FMZ TA library.** `TA.MA` = simple MA, `TA.EMA` = EMA seeded with the first value
  (pandas `ewm(adjust=False)`), `TA.RSI`/`TA.ATR` = Wilder smoothing (RMA seeded with an SMA),
  matching TA-Lib, which FMZ wraps.
- **Port order.** Ports are made in ascending FMZ id over the admitted, deduplicated set.
  This is a neutral order and implies nothing about merit.

## MyLanguage (麦语言) interpretation rules (added 2026-10-07, worker A)

Fixed before the first MyLanguage port, applied to all of them.

- **Evaluation model.** FMZ MyLanguage's default is the close-price model: every statement is
  evaluated once when a bar completes, and orders go out right after, i.e. at the next bar's open.
  That is the contract exactly. Scripts that switch to intrabar evaluation (`MULTSIG`, real-time
  model) are ported on completed bars (same rule as bots polling the forming bar), and say so.
- **Functions.** `C/O/H/L` = the current bar; `REF(X,n)` = `X.shift(n)`; `MA` = simple MA;
  `EMA(X,N)` = `ewm(span=N, adjust=False)` (seeded with the first value); `SMA(X,N,M)` =
  `ewm(alpha=M/N, adjust=False)`; `DMA(X,A)` = `Y = A*X + (1-A)*Y'` with a Series `A`;
  `HHV/LLV(X,N)` = rolling max/min over N bars INCLUDING the current bar; `HV/LV(X,N)` = the same
  over the N bars BEFORE the current bar (`HHV(X,N).shift(1)`); `SUM(X,N)` = rolling sum;
  `CROSSUP(A,B)` = `A > B and A[1] <= B[1]`, `CROSSDOWN` mirror; `BARPOS` = 1-based bar number.
  Rolling windows have no value until N bars exist (no partial-window values).
- **Position words.** `BK`/`SK` open long/short; `SP`/`BP` close long/short; `BPK`/`SPK` close the
  opposite side and open (a one-bar reversal: `REVERSAL INTENDED`); `CLOSEOUT` closes all.
  `BKVOL>0` = long held; `ISLASTBK` = the latest signal was `BK`.
- **AUTOFILTER** (and explicit `BKVOL=0`/`ISLAST...=0` guards): an opening signal is valid only
  from flat (or as `BPK`/`SPK`), and at most one signal per bar, the first valid statement in
  source order winning. Without AUTOFILTER, a repeated `BK` while long is an add (pyramiding:
  sizing, criterion 4, not ported); a `BK` while short would hold both sides on FMZ, which a
  net-position contract cannot hold, so the port ignores it (`upon_opposite_entry="ignore"` and
  the port's own position tracking).
- **BKPRICE / SKPRICE** = the price of the latest `BK`/`SK` signal, i.e. that signal bar's close
  under the close-price model (adds included, since the source's stop refers to them);
  `BKHIGH`/`SKLOW` = highest high / lowest low of the bars after that signal bar.
- **Exits.** `SP`/`BP` statements, including the authors' "stop loss" lines (`C<=BKPRICE*(1-x%)`,
  `LOW<=...`), are conditions on the completed bar, so they are exit signals from `simulate()`,
  not `sl_stop` (rule 3 by analogy). Percent distances become ATR multiples (criterion 2):
  the source's own ATR if it has one, else Wilder ATR(14), taken on the reference signal bar.
- Money words (`MONEYTOT`, lot formulas, `TRADE_AGAIN`, `MULTSIG` counts, `SETSIGPRICETYPE`) are
  sizing/execution: quoted in `original_sizing.txt`.

## Screening method (criteria 1, 2, 3, 6), `survey_tools/screen.py`

Static regular-expression rules over comment-stripped source code only (descriptions are not
read). Outcomes per criterion: `PASS`, `ADAPT` (passes after re-expressing price units as ATR
multiples), `REVIEW` (settled by reading at port time), `FLAG` (criterion 3), `FAIL`.
Overall outcome, in priority order: `FLAGGED_CRYPTO_ONLY`, `REJECTED` (criterion 1 or 2 FAIL),
`DUPLICATE` (not the representative of its group), `HELD_NEEDS_VOLUME`, `PORT_CANDIDATE`.

Near-duplicates (criterion 6): source is normalised (strings, plot/label/alert lines and
cosmetic keyword arguments removed, numbers replaced by 0), cut into 5-token shingles, and
compared by exact Jaccard similarity within the same language. Pairs at >= 0.80 are merged
(union-find); pairs at 0.65-0.80 go to `possible_duplicates.csv`. The representative of a group
is the member with the best screening status, then the lowest FMZ id (earliest published).
Collapsing is by code, never by performance.

Screening outcomes marked `REVIEW` are provisional. The final per-file outcome is the one in
`review_decisions.csv` (for files read and rejected) or the port's `PORT_NOTES.md`.
