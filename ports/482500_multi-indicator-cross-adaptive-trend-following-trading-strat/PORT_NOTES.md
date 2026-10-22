# #482500 Multi Indicator Cross Adaptive Trend Following Trading Strategy -> `fmz_482500_ema6_20_cross_lsma333_rsi50_pct_bracket_reversal`

- FMZ source id: 482500 (lineage).
- Source: https://www.fmz.com/strategy/482500 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 17:17:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C246). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the signal close as fractions of the fill |
| 2 | PASS | EMA crossings with a long regression-line side and RSI filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss_perc` [1.0, 3.0] x `take_profit_perc` [2.0, 6.0]: **4 trials**; EMA 6 / 20, LSMA 333, RSI 14.

## Ambiguities resolved

- A repeat crossing's re-sent bracket is pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
