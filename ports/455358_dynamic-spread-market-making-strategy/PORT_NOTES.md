# #455358 Dynamic Spread Market Making Strategy -> `fmz_455358_sma14_spread_band_counter_reversal`

- FMZ source id: 455358 (lineage).
- Source: https://www.fmz.com/strategy/455358 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-28 15:08:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C197). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA band reversion with an order counter |
| 3 | PASS | No exchange named. |
| 4 | DONE | The quantity 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 50] x `spread_pct` [0.1, 0.5]: **4 trials**; the limit 100 and the offset fixed.

## Ambiguities resolved

- No bar size (bar_size_pending); the counter counts calls. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`bar_size_pending`
