# #490795 Multi Signal Convergence Cloud Edge Breakout Strategy -> `fmz_490795_ichimoku_eight_check_consensus_reversal`

- FMZ source id: 490795 (lineage).
- Source: https://www.fmz.com/strategy/490795 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-16 15:24:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C273). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku consensus states |
| 3 | PASS | Futures exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bullishThreshold` [8, 7] x `bearishThreshold` [0, 1]: **4 trials**; Ichimoku 9 / 26 / 52 / 26.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
