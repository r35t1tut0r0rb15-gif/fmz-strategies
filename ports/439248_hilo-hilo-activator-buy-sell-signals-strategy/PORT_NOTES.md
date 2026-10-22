# #439248 Hilo激活器买卖信号策略Hilo-Activator-Buy-Sell-Signals-Strategy -> `fmz_439248_hilo_activator_close_cross`

- FMZ source id: 439248 (lineage).
- Source: https://www.fmz.com/strategy/439248 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-18 15:56:51). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C119). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close / activator line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [8, 13] x `shift` [1, 2]: **4 trials**; SMA averages fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
