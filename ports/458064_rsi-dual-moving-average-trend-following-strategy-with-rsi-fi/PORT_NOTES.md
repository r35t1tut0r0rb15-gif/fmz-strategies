# #458064 双均线趋势跟踪策略与RSI过滤器-Dual-Moving-Average-Trend-Following-Strategy-with-RSI-Filter -> `fmz_458064_sma200_confirmed_rsi30_dip_late_ref_close_tests_long`

- FMZ source id: 458064 (lineage).
- Source: https://www.fmz.com/strategy/458064 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 16:45:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C200). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the exits are close tests |
| 2 | PASS | RSI dips in a confirmed SMA uptrend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [200, 100] x `confirm` [30, 12] x `tp_pct` [0.02, 0.01]: **8 trials**; the 0.5 % stop and RSI 30 fixed.

## Ambiguities resolved

- Exit levels from the first signal after the fill (as written). Long only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
