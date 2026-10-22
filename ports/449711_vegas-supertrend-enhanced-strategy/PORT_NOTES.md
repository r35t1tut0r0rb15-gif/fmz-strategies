# #449711 Vegas SuperTrend Enhanced Strategy -> `fmz_449711_vegas_adjusted_supertrend_state_reversal`

- FMZ source id: 449711 (lineage).
- Source: https://www.fmz.com/strategy/449711 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-28 13:43:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C180). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volatility-adjusted SuperTrend direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The cash size stored; the commission and slippage are costs, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`base_mult` [5.0, 3.0] x `vol_adj` [5.0, 2.0]: **4 trials**; the ATR period and the Vegas window fixed.

## Ambiguities resolved

- Long from the first bar (trend starts at 1). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
