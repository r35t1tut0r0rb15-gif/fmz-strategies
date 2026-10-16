# #428797 Heiken Ashi Bar Color Change Strategy -> `fmz_428797_heikin_ashi_colour_change`

- FMZ source id: 428797 (lineage).
- Source: https://www.fmz.com/strategy/428797 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-09 15:38:46). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Candle colour only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`confirm` [1, 2]: **2 trials** (declared starting variants; 1 is the source).

## Ambiguities resolved

- No inputs: two declared variants (criterion 5). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi_trend"`.

## Marks

`none`
