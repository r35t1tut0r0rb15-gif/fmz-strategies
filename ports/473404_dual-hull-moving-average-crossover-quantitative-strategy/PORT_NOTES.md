# #473404 Dual Hull Moving Average Crossover Quantitative Strategy -> `fmz_473404_hma9_16_cross_reversal`

- FMZ source id: 473404 (lineage).
- Source: https://www.fmz.com/strategy/473404 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 16:53:05). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C219). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Hull MA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [16, 30]: **4 trials**.

## Ambiguities resolved

- n / 2 floored. REVERSAL INTENDED. FREQ = "2D" (blocks of 2 broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "hull_ma"`.

## Marks

`none`
