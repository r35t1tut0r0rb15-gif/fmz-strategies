# #431224 Trend Following Strategy -> `fmz_431224_ha_ema_hma_long`

- FMZ source id: 431224 (lineage).
- Source: https://www.fmz.com/strategy/431224 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-06 10:34:19). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits |
| 2 | PASS | Moving averages and a percentage stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 15 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hma_len` [69, 34] x `stop_pct` [6.5, 3.0]: **4 trials**; EMA 9 and the HA source fixed.

## Ambiguities resolved

- Close-checked stop and profit exit from the fill price. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
