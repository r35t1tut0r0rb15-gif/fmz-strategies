# #458201 Multi EMA Crossover Momentum Strategy -> `fmz_458201_ema13_30_cross_ema100_side_reversal`

- FMZ source id: 458201 (lineage).
- Source: https://www.fmz.com/strategy/458201 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 17:20:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C203). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with a long-EMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [13, 9] x `slow` [30, 50] x `trend` [100, 200]: **8 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
