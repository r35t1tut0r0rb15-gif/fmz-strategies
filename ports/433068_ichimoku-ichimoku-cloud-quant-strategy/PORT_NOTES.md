# #433068 Ichimoku云图量化策略Ichimoku-Cloud-Quant-Strategy -> `fmz_433068_ichimoku_long_ema_filter`

- FMZ source id: 433068 (lineage).
- Source: https://www.fmz.com/strategy/433068 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-24 10:15:15). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C58). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku lines, candle colour and EMA order |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema1` [24, 12] x `ema2` [90, 50]: **4 trials**; Ichimoku 9 / 26 / 52 fixed.

## Ambiguities resolved

- Lead lines unshifted as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
