# #429493 EMA and Heikin Ashi Trading Strategy -> `fmz_429493_ha_close_ema15_50`

- FMZ source id: 429493 (lineage).
- Source: https://www.fmz.com/strategy/429493 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-17 16:11:19). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Moving-average comparisons only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1` [15, 10] x `ma2` [50, 100]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi_trend"`.

## Marks

`none`
