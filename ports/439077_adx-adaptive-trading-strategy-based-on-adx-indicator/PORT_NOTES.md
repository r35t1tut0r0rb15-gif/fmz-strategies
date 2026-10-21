# #439077 基于ADX指标的自适应交易策略Adaptive-Trading-Strategy-Based-on-ADX-Indicator -> `fmz_439077_adx_between_di_lines`

- FMZ source id: 439077 (lineage).
- Source: https://www.fmz.com/strategy/439077 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-17 15:33:37). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C116). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ADX position against the DI lines |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 15-contract quantity and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG439077. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [14, 21] x `diff` [10, 5]: **4 trials**; long and short gaps swept together.

## Ambiguities resolved

- The source's ADX sums. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`none`
