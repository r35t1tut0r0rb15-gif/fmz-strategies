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
6. Near-duplicates are collapsed to one representative, and the others are listed.
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
| `ports/<fmz_id>_<slug>/module.py` | the port |
| `ports/<fmz_id>_<slug>/original_source.md` | verbatim copy of the FMZ file |
| `ports/<fmz_id>_<slug>/original_sizing.txt` | verbatim sizing / money-management code with line references (criterion 4) |
| `ports/<fmz_id>_<slug>/PORT_NOTES.md` | outcome of each of the 7 criteria, declared GRID and why, ambiguities resolved |
| `flagged/<fmz_id>_<slug>/` | criterion 3: `original_source.md` (verbatim) + `REASON.md`; not ported |
| `survey_tools/` | the static screening scripts (read text only; never execute strategies) |

Line references in `original_sizing.txt` are line numbers in `original_source.md`.

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
`portfolio_kwargs` must then be empty.

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
- **FMZ TA library.** `TA.MA` = simple MA, `TA.EMA` = EMA seeded with the first value
  (pandas `ewm(adjust=False)`), `TA.RSI`/`TA.ATR` = Wilder smoothing (RMA seeded with an SMA),
  matching TA-Lib, which FMZ wraps.
- **Port order.** Ports are made in ascending FMZ id over the admitted, deduplicated set.
  This is a neutral order and implies nothing about merit.

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
