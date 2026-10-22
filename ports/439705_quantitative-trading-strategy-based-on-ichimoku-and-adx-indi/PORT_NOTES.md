# #439705 Quantitative Trading Strategy Based on Ichimoku and ADX Indicators -> `fmz_439705_ichimoku_fresh_alignment_adx20`

- FMZ source id: 439705 (lineage).
- Source: https://www.fmz.com/strategy/439705 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-23 11:14:54). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C123). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit margins -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [20, 25] x `base` [26, 30]: **4 trials**; conversion 9, span B 52, displacement 26 fixed.

## Ambiguities resolved

- Price-unit margins as fractions of the close. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
