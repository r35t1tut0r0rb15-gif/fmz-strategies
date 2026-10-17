# #433021 RSI轴向均线交叉策略RSI-Axial-Moving-Average-Crossover-Strategy -> `fmz_433021_rsi_sma_cross`

- FMZ source id: 433021 (lineage).
- Source: https://www.fmz.com/strategy/433021 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-23 16:45:55). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C57). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An oscillator against its own average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `ma_len` [14, 28]: **4 trials**; MA type SMA fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
