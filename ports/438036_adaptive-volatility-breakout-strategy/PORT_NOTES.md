# #438036 Adaptive Volatility Breakout Strategy -> `fmz_438036_log_range_breakout_one_day`

- FMZ source id: 438036 (lineage).
- Source: https://www.fmz.com/strategy/438036 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-08 14:38:31). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C108). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Log-range breakout level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k` [0.6, 0.4, 0.8, 0.5]: **4 trials**.

## Ambiguities resolved

- hour == 0 true on every daily bar: one-bar holds. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
