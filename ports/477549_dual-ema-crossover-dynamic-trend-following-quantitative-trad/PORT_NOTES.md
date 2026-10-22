# #477549 Dual EMA Crossover Dynamic Trend Following Quantitative Trading Strategy -> `fmz_477549_ema20_50_cross_reversal`

- FMZ source id: 477549 (lineage).
- Source: https://www.fmz.com/strategy/477549 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 13:42:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C233). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100]: **4 trials**.

## Ambiguities resolved

- The limit exits are replaced by the same-bar reversal and never act. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
