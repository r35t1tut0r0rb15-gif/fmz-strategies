# #468309 Dynamic Trend Following Strategy with Machine Learning Enhanced Risk Management -> `fmz_468309_sma20_50_cross_rsi_half_filter_prev_avg_atr_stop_reversal`

- FMZ source id: 468309 (lineage).
- Source: https://www.fmz.com/strategy/468309 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 14:58:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C206). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the replaced position's price as the stop base, as written |
| 2 | PASS | SMA crossings with an RSI half filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [20, 10] x `long_len` [50, 100] x `sl_mult` [2.0, 3.0]: **8 trials**.

## Ambiguities resolved

- Stop base is the replaced position's average price (na from flat); trails never act (as written). REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
