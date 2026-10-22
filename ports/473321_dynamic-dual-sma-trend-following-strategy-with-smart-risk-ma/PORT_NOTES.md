# #473321 Dynamic Dual SMA Trend Following Strategy with Smart Risk Management -> `fmz_473321_sma20_high_low_slope_recross_bracket_reversal`

- FMZ source id: 473321 (lineage).
- Source: https://www.fmz.com/strategy/473321 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 11:06:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C216). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the replaced position's price as the target base, as written |
| 2 | PASS | SMA-of-extremes re-crossings with a slope filter and a bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_period` [20, 50] x `tp_pct` [0.05, 0.10] x `sl_pct` [0.01, 0.02]: **8 trials**; the slope threshold fixed.

## Ambiguities resolved

- Target from the replaced position's price (na from flat), as written; repeat-signal re-sends not followed (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
