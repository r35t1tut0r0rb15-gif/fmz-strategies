# #439693 This strategy is a momentum strategy based on moving average lines -> `fmz_439693_sma13_34_cross_percent_bracket_long`

- FMZ source id: 439693 (lineage).
- Source: https://www.fmz.com/strategy/439693 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-23 10:38:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C122). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed from the fill |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.10, 0.05] x `tp` [0.30, 0.15]: **4 trials**; the SMA pairs fixed.

## Ambiguities resolved

- Bracket from the fill. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
