# #483051 动态流动性级联捕捉策略-Dynamic-Liquidity-Cascade-Capture-Strategy -> `fmz_483051_distance_extreme_cascade_long`

- FMZ source id: 483051 (lineage).
- Source: https://www.fmz.com/strategy/483051 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-24 15:16:23). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Distance from moving averages in percent and rolling extremes. |
| 3 | PASS | Exchange pair in the header only; no liquidation data is used. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`window` [89, 55] x `exit_level` [-1.0, 0.0]: **4 trials**; defaults 89 / -1 (the source's); SMA 15 / EMA 30 fixed.

## Ambiguities resolved

- `valuewhen(longLiq, longLiq, k)` is true whenever a k-th earlier longLiq bar exists, so the buy condition holds on
  every bar after the third longLiq bar, as written.
- `close < close - 2 ATR` is never true: inert. Closes act on the position held at the bar's start (as #430850); the
  result alternates in and out while the distance stays above -1 %, as written.
- Long only: opposite entries cannot occur. No stops. Broker days stamped with their first minute (as #430984).
  FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
