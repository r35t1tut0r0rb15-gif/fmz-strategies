# #428813 ATR Trailing Stops Strategy -> `fmz_428813_atr_trailing_line_long`

- FMZ source id: 428813 (lineage).
- Source: https://www.fmz.com/strategy/428813 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-09 16:59:57). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An ATR multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_period` [5, 10] x `mult` [3.5, 2.5]: **4 trials**; shorts off fixed.

## Ambiguities resolved

- Before the ATR exists the line is na and then restarts from 0 (nz). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
