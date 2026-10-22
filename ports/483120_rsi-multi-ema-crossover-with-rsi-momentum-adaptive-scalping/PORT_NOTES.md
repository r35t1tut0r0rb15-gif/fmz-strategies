# #483120 多重均线交叉与RSI动量联动短线自适应交易策略-Multi-EMA-Crossover-with-RSI-Momentum-Adaptive-Scalping-Strategy -> `fmz_483120_ema9_21_cross_ema50_side_rsi_band_pct_bracket_reversal`

- FMZ source id: 483120 (lineage).
- Source: https://www.fmz.com/strategy/483120 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 14:27:45). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C258). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | EMA crossings with an EMA side and RSI bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss_percent` [0.5, 1.0] x `target_percent` [1.0, 2.0]: **4 trials**; EMA 9 / 21 / 50, RSI 14.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
