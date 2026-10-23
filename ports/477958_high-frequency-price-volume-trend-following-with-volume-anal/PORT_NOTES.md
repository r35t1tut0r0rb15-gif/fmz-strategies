# #477958 High Frequency Price Volume Trend Following with Volume Analysis Adaptive Strategy -> `fmz_477958_momentum6_sma50_close_location_rolling_stop_reversal`

- FMZ source id: 477958 (lineage).
- Source: https://www.fmz.com/strategy/477958 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-10 15:42:31). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V37). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar re-sent stop and target followed in the signals |
| 2 | PASS | Short-term momentum in the SMA 50 trend with close-location filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.03, 0.05] x `tp` [0.29, 0.1]: **4 trials**; SMA 50, lookback 6.

## Ambiguities resolved

- Volume cancels out. Re-sent stop / target followed at the next open. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum"`.

## Marks

`trailing_stop_pending`
