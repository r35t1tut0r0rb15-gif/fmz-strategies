# #434299 Cross Moving Average Golden Cross Death Cross Strategy -> `fmz_434299_ichimoku_twist_long`

- FMZ source id: 434299 (lineage).
- Source: https://www.fmz.com/strategy/434299 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-05 11:11:02). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C66). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku lines and cloud twists |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tenkan` [9, 20] x `cooldown` [5, 0]: **4 trials**; Kijun 26, Senkou B 52 fixed, the Chikou check off.

## Ambiguities resolved

- Cooldown on the surviving signals (loop). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
