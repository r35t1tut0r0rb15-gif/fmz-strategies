# #473386 Dual EMA Dynamic Zone Trend Following Strategy -> `fmz_473386_cdc_action_zone_ema12_26_long`

- FMZ source id: 473386 (lineage).
- Source: https://www.fmz.com/strategy/473386 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 16:12:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C218). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA action zones |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Fixed qty, commission and slippage stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `slow` [26, 50]: **4 trials**; smoothing 1, fixed-timeframe mode off.

## Ambiguities resolved

- Fixed-timeframe mode off (default). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
