# #468299 Multi Indicator Synergy Long Term Trading Strategy -> `fmz_468299_red_candle_run_dip_sma200_sar_sma5_doji_exits_long`

- FMZ source id: 468299 (lineage).
- Source: https://www.fmz.com/strategy/468299 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 14:32:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C206). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the percent bracket as fixed fractions |
| 2 | PASS | Red-candle dips in an uptrend with SAR, SMA and doji exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`open_count` [3, 2] x `bracket` [0.005, 0.02] x `ma_len` [200, 100]: **8 trials**; the exit switches on.

## Ambiguities resolved

- Opening bracket kept on repeat signals (trailing_stop_pending). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
