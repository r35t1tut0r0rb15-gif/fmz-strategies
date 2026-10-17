# #432305 Momentum Ichimoku Cloud Trading Strategy -> `fmz_432305_sma_ichimoku_cross_long`

- FMZ source id: 432305 (lineage).
- Source: https://www.fmz.com/strategy/432305 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-16 10:56:22). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C51). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crosses and lagged spans |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conv` [9, 7] x `disp` [26, 13]: **4 trials**; base 26 and span B 52 fixed.

## Ambiguities resolved

- SMA lines as written; spans 26 bars back. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
