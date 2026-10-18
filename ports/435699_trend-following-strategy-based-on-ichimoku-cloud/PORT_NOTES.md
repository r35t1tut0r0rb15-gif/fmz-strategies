# #435699 Trend Following Strategy Based on Ichimoku Cloud -> `fmz_435699_chikou_displaced_lines_long`

- FMZ source id: 435699 (lineage).
- Source: https://www.fmz.com/strategy/435699 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-18 10:20:01). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C80). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku lines |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tenkan` [9, 7] x `kijun` [26, 22]: **4 trials**; displacement 26 fixed.

## Ambiguities resolved

- All terms displaced 26 bars (delayed signal). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
