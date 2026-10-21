# #437383 Parameter Optimized Trend Following Quantitative Strategy -> `fmz_437383_percent_rank_level_cross`

- FMZ source id: 437383 (lineage).
- Source: https://www.fmz.com/strategy/437383 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-02 11:01:22). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C100). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Percent rank levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20] x `level` [30.0, 20.0]: **4 trials**; the levels are +-level around the scale offset 50.

## Ambiguities resolved

- Level crossings reverse the position. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
