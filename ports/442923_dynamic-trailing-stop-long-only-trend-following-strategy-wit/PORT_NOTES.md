# #442923 Dynamic Trailing Stop Long Only Trend Following Strategy with Seasonality Filter -> `fmz_442923_adx27_cross_di_atr_stop_long`

- FMZ source id: 442923 (lineage).
- Source: https://www.fmz.com/strategy/442923 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 14:01:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C162). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the ratchet pending |
| 2 | PASS | ADX threshold crossing with DI direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_threshold` [27.0, 20.0] x `atr_mult` [5.5, 3.0]: **4 trials**; the DI and ATR lengths fixed.

## Ambiguities resolved

- Initial ATR stop from the signal bar; the ratchet pending. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`trailing_stop_pending`
