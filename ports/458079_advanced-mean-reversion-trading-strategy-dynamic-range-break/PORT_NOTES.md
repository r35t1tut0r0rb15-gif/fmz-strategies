# #458079 Advanced Mean Reversion Trading Strategy Dynamic Range Breakout System Based on Standard Deviation -> `fmz_458079_sma30_2sd_band_touch_mean_exit_reversal`

- FMZ source id: 458079 (lineage).
- Source: https://www.fmz.com/strategy/458079 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 17:16:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C201). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band touches with a return to the mean |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [30, 20] x `k` [2.0, 2.5]: **4 trials**.

## Ambiguities resolved

- Call order followed (entries, then closes). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
