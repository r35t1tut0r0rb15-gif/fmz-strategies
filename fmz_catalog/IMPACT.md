# How much of the FMZ library uses indicator code that should change

**Short answer:** 169 of 5,806 strategies (2.9%) have indicator code that
really should change: 121 have a bug and 48 use future data. Another 195
(3.4%) use a deliberate variant of a standard indicator, which is fine to
keep but needs the matching variant template. The remaining 94% either
already compute the best version (4,819, 83.0%), differ only during warm-up
(78, 1.3%), or use no indicators at all (545, 9.4%).

| Category | Strategies | Share | What it means when we port to the templates |
|---|---|---|---|
| Matches best version | 4,819 | 83.0% | Swap in the templates; the results stay the same |
| Warm-up only | 78 | 1.3% | Seeds differ (e.g. `nz(x[1])` = 0 instead of an SMA seed). Swapping changes only the first bars |
| Variant | 195 | 3.4% | A legitimate but different formula (ADX = SMA(DX), Kivanc ZLEMA lag, Ehlers vs Cycle-Analytics SSF, HPotter simplifications...). Keep it, using the variant option or function in the staging code |
| **Bug** | **121** | **2.1%** | The code computes something persistently different from the indicator it claims to be. Should change |
| **Look-ahead** | **48** | **0.8%** | Uses data from the future, mostly `security(..., lookahead_on)` without `[1]`. Backtest results are unreliable; must change |
| No indicators | 545 | 9.4% | Grid/DCA/arbitrage bots, pure price action, timers |

All 169 bug and look-ahead strategies are Pine scripts (FMZ's Pine engine
runs 5,283 of the 5,806). The 523 JavaScript / Python / MyLanguage / C++
strategies mostly call FMZ's `TA.*` / `talib.*` libraries or MyLanguage
built-ins. Those work as documented, but some differ from TradingView (see
CATALOG.md, "FMZ's own functions"). That only matters when porting them, and
they are not counted as bugs.

Per-strategy results, with the reason for each verdict:
[impact_by_strategy.csv](impact_by_strategy.csv). Counts by indicator:
[IMPACT.json](IMPACT.json).

## The bugs (121 strategies)

18 of the 121 are latent. The bug sits in one option of a moving-average
selector (e.g. the "SMMA" choice that recurses on the WMA's previous
value), and it only matters if a strategy picks that option. The other 103
are in code that runs.

The most common, by number of strategies:

- **Supertrend copies (11):**
  - band ratchets that never flip or are inverted
  - an "LWST" that compares close with its own ±1 flag
  - `close[2]` used in the ratchet
  - the upper band resetting to the lower one
- **MA selectors (18, latent):**
  - SMMA recursing on WMA[1]
  - an "LSMA" that returns the price unchanged
  - TMA = sma(sma(n), n)
  - "WMA" with constant weights
- **Hand-written ATR / ADX / DMI (about 10):**
  - "ATR" computed as mean |close − close[1]|
  - DI divided by a single bar's TR
  - "ADX" returned as raw DX
  - an HTF ATR that steps on every chart bar
- **Highest/lowest loops that cover length+1 bars (6).**
- **Williams A/D (3):** uses low[1]/high[1] instead of the true range, or resets on unchanged closes.
- **Sine WMA (3):** weights start at sin(0), so the current bar is ignored.
- **Renko emulators (3):** zero-seeded, moving at most one brick per bar, so they lag price for hundreds of bars.
- **OLS "linregs" (3):** each bar uses its own rolling mean, so it isn't a regression.
- **HPotter Prime Number Oscillator / Bands (4):** a float loop counter means no prime is ever found. One combo never trades; the other becomes a 5-bar breakout.
- **HPotter FVE / Volatility FVE (4):** a running total where Katsanos uses a rolling one, and the wrong stdev.
- **G-Channel (2):** buy and sell crosses reversed, so every trade is flipped.
- **Kernel regression copies (2):** the oldest bar gets the most weight.
- **Others, 1–2 each:**
  - Blackflag FTS: a constant 50
  - Hurst: not R/S
  - RedK VADER: altered copies
  - eVWMA: not recursive
  - session VWMA: off by one
  - Ehlers zero-lag EC: the gain search never runs
  - Hilbert period: decays to 0
  - Butterworth: mixed coefficients
  - Super Passband: RMS 12% too wide
  - BigBeluga VIDYA: trend state reset every bar
  - KAMA: wrong efficiency ratio
  - T3: wrong EMA chain
  - "TEMA" that is really DEMA
  - and similar

Each bug's snippet id, files and exact defect are in
`scan/review/result_*.jsonl` (verdict `bug`) and `scan/impl/*_report.json`
(`strategy_issues`).

## Look-ahead (48 strategies)

- **44:** `security()` / `request.security()` with `lookahead_on`, or
  `lookahead=true`, without the `[1]` offset. On historical bars this reads
  the higher-timeframe bar's final value before it closes.
- **4:** a higher-timeframe Ichimoku, MACD histogram, RSI or momentum wave
  done the same way inside a function.

A further 91 v1/v2 or unversioned scripts call `security()` with no
look-ahead setting at all. Their default could not be confirmed, so they
are **not** counted here; check them before trusting their backtests.

## Variants (195 strategies), keep but use the right template

The most common:

| Variant | Strategies | Use |
|---|---|---|
| ZLEMA lag floor(n/2) (Kivanc) instead of (n−1)/2 | 25 | `fx.zlema_half_lag` |
| ADX = SMA(DX) ("ADX and DI", BeikabuOyaji) | 16 | `fx.adx_sma` |
| Supertrend flavours (Kivanc's flip test, close[2]) | 14 | `ti.supertrend_kivanc` (+ options) |
| SuperSmoother without the input average (Cycle Analytics) | 13 | `fx.ssf2` |
| KAMA constants / MAMA-limited KAMA | 10 | `ti.kama`, and the `extra_hpotter` KAMA option |
| Fractals with ties (RicardoSantos) | 8 | `extra_tv` / `ti.fractals` options |
| TRIMA as sma(sma(n), n) | 8 | documented in the staging code |

Many HPotter variants are covered by `hpotter=True` options in
`extra_hpotter`: Fisher feedback, ADXR lag, additive PVI/NVI, CCI on close,
and others. HPotter's 314 strategies were graded separately:
225 standard, 60 variant, 22 bug, 7 warm-up only.

## On our side: one template to fix

TradingView's current Hull MA floors √length, while `ti.hma` rounds it (see
CATALOG.md). This is the one place where the FMZ strategies are right and
our template would change their results. 110 strategies call `hma()`
(about 240 use some Hull average). Fix `ti.hma` before porting them.

## How this was measured

1. **Inventory:** [scan/detect.py](scan/detect.py) tags each strategy with
   the indicators it uses: built-in calls, custom function names and formula
   fingerprints.
2. **Custom code review:** [scan/snippets.py](scan/snippets.py) extracts
   custom indicator code from all Pine strategies: user functions, recursive
   series lines and loops over past bars. It found 3,583 unique snippets in
   1,873 strategies after deduplication. Six reviewers graded every snippet
   against the best definition (`scan/review/result_*.jsonl`). The grading
   was checked for misfiled rows: correct pairs score 42% on a code-vs-label
   heuristic, shuffled pairs 2%, and every 50-row window scored at least 25%.
3. **Implementation:** the implementation agents ported each missing
   indicator from its source with bar-by-bar tests. Bugs they found in
   strategy copies were added to the count, graded by severity in
   [scan/build_docs.py](scan/build_docs.py). Trivia such as π = 3.14 is
   counted as warm-up only, not as a bug.
4. **Look-ahead:** found by a regex for `security(..., lookahead_on)`
   without `[1]`.
5. **Each strategy** gets its single worst verdict:
   look-ahead > bug > variant > warm-up > standard.

**Limits:**
- **Unaudited built-ins:** built-in `ta.*` calls are assumed correct, because
  FMZ documents TradingView's formulas. Nothing was checked against FMZ's or
  TradingView's live output.
- **Missed custom code:** custom indicator code that matched none of the
  extraction patterns, such as inline arithmetic with no recursion or loop,
  was not reviewed.
- **Reviewer judgement:** the reviewers' verdicts are judgement calls. The
  bug verdicts were spot-checked and held up.
- **Execution layer not counted:** fills, fees and sizing are left out.
  FMZ's execution layer differs from TradingView in ways that change
  backtest results (fees in `position_avg_price`, a simulated spread, OCA
  not supported, most `strategy()` settings ignored). That is a separate
  question from indicator code.
