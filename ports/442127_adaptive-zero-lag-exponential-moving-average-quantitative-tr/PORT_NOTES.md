# #442127 Adaptive Zero Lag Exponential Moving Average Quantitative Trading Strategy -> `fmz_442127_zero_lag_ema_cross_error_filter_tick_trail`

- FMZ source id: 442127 (lineage).
- Source: https://www.fmz.com/strategy/442127 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-19 15:38:02). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C152). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is a house trail (approximation stated) |
| 2 | ADAPT | Tick stop and trail -> ATR multiples and a fraction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based lot size and the tick inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [20, 40] x `threshold` [0.05, 0.1]: **4 trials**; the tick exits fixed.

## Ambiguities resolved

- Tick stop / trail as ATR multiples at the 4-hour reading (stated approximation). REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "adaptive_average"`.

## Marks

`coarse_bar_stop, trailing_stop`
