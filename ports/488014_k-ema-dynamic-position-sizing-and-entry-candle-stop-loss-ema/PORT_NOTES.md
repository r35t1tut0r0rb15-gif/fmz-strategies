# #488014 动态仓位与入场K线止损的EMA交叉策略-Dynamic-Position-Sizing-and-Entry-Candle-Stop-Loss-EMA-Crossover-Strategy -> `fmz_488014_ema10_20_cross_bull_candle_low_stop_long`

- FMZ source id: 488014 (lineage).
- Source: https://www.fmz.com/strategy/488014 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-24 14:04:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C264). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar low stop as a fraction of the fill |
| 2 | PASS | EMA crossings with a candle-low stop |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Risk-sized quantity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 5] x `slow` [20, 50]: **4 trials**.

## Ambiguities resolved

- Same-side re-sends are pending. Long only. FREQ = "1h". MPL 2.0.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
