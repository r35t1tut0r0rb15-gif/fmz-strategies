# #483066 动态趋势突破型指数平滑移动均线交叉策略-Dynamic-Trend-Breakthrough-Exponential-Moving-Average-Crossover-Strategy -> `fmz_483066_ema33_cross_swing_bracket_1d`

- FMZ source id: 483066 (lineage).
- Source: https://www.fmz.com/strategy/483066 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:05:44). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | An EMA and rolling swing extremes. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND482870 (2 members, best partner #482870, Jaccard 0.746). |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [33, 50] x `swing_len` [14, 20]: **4 trials**; defaults 33 / 14 (the source's).

## Trailing stop (mark `trailing_stop_pending`)

Every close below EMA 33 is a sell signal, so a held short has its stop and target re-placed from each new bar's swing
levels. The port keeps the entry's bracket.

## Ambiguities resolved

- The swing levels become fractions of the signal close by side, re-based on the fill; a signal whose stop or target
  is not beyond the close emits no entry (as #490798). A long and a short signal cannot meet on one bar.
- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4).
- Broker days stamped with their first minute (as #430984); stops on daily bars: `coarse_bar_stop`. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
