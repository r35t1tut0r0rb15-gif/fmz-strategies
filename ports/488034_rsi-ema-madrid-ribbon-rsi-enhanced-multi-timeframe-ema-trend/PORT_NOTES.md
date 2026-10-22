# #488034 马德里带状RSI增强型多时框EMA趋势策略-Madrid-Ribbon-RSI-Enhanced-Multi-Timeframe-EMA-Trend-Strategy -> `fmz_488034_madrid_ribbon_count_rsi_extreme_pct_bracket_reversal`

- FMZ source id: 488034 (lineage).
- Source: https://www.fmz.com/strategy/488034 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-24 15:52:28). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C264). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | EMA ribbon counts with RSI extremes and a percent bracket |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | Cash quantity (100000 / close) stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_take_profit_perc` [0.5, 2.0] x `long_stop_loss_perc` [1.0, 3.0]: **4 trials** (the short side uses the same values); RSI 14, counts 13 / 9.

## Ambiguities resolved

- ta.change in the loop reads the previous bar's EMA 90 (flagged reading). Repeat-state re-sends are pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_ribbon"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
