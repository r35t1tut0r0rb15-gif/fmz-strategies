# #435966 Logarithmic Price Forecasting Strategy -> `fmz_435966_logistic_forecast_signed_volume_z_long`

- FMZ source id: 435966 (lineage).
- Source: https://www.fmz.com/strategy/435966 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-20 14:40:23). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume-z-driven logistic forecast against the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`std_len` [20, 50] x `net_len` [100, 50]: **4 trials**; SMA 10, 1.005 / 0.995.

## Ambiguities resolved

- Signed volume as the loop leaves it. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_state"`.

## Marks

`none`
