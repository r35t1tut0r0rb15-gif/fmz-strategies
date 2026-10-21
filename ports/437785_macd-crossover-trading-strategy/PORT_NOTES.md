# #437785 MACD Crossover Trading Strategy -> `fmz_437785_macd_hist_zero_cross_long`

- FMZ source id: 437785 (lineage).
- Source: https://www.fmz.com/strategy/437785 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-05 15:32:06). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C106). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD histogram crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 12] x `slow` [40, 26]: **4 trials**; signal 4 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
