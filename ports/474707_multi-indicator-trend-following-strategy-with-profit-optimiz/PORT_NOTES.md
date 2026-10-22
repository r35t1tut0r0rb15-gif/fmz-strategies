# #474707 Multi Indicator Trend Following Strategy with Profit Optimization -> `fmz_474707_sar_break_sma50_dmi_target_close_long`

- FMZ source id: 474707 (lineage).
- Source: https://www.fmz.com/strategy/474707 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 17:22:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C223). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SAR breaks with SMA / DMI filters and a target close; resting limit described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [50, 100] x `target_pct` [3.0, 6.0]: **4 trials**; SAR / DMI / MACD settings fixed.

## Ambiguities resolved

- The MACD-armed resting limit is pending (trailing_stop_pending). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`trailing_stop_pending`
