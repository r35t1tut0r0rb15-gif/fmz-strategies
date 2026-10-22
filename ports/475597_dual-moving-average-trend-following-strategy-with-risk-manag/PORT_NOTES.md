# #475597 Dual Moving Average Trend Following Strategy with Risk Management -> `fmz_475597_ema110_250_cross_1pct_stop_half_pct_target_reversal`

- FMZ source id: 475597 (lineage).
- Source: https://www.fmz.com/strategy/475597 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-20 14:30:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C228). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar bracket as fractions of the fill |
| 2 | PASS | EMA crossings with a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

No parameter reaches the orders: **1 trial**, the source as written (all lengths and percents are constants).

## Ambiguities resolved

- EMA 250 under an "EMA 200" label, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
