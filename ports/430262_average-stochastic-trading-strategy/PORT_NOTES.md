# #430262 Average Stochastic Trading Strategy -> `fmz_430262_avg_stochastic`

- FMZ source id: 430262 (lineage).
- Source: https://www.fmz.com/strategy/430262 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-26 16:20:33). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; adds not ported. |
| 2 | PASS | Stochastic levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Pyramiding 3 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period_k` [21, 14] x `smooth_k` [3, 5]: **4 trials**; %D 3 and levels 20 / 80 fixed.

## Ambiguities resolved

- Adds not ported. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
