# #430142 Ichimoku Balance Line trend following Strategy -> `fmz_430142_tk_state_above_ema200_long`

- FMZ source id: 430142 (lineage).
- Source: https://www.fmz.com/strategy/430142 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-25 14:32:23). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Channel midpoints and a moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Initial_capital / close per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion` [20, 9] x `base` [60, 26]: **4 trials**; EMA 200 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
