# #490795 多重信号一致性云层边缘突破策略-Multi-Signal-Convergence-Cloud-Edge-Breakout-Strategy -> `fmz_490795_ichimoku_eight_signal_vote`

- FMZ source id: 490795 (lineage).
- Source: https://www.fmz.com/strategy/490795 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-16 15:24:06). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; all series from past bars. |
| 2 | PASS | Ichimoku comparisons |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bull_threshold` [8, 7] x `bear_threshold` [0, 1]: **4 trials**; defaults 8 / 0 (the source's); Ichimoku 9 / 26 / 52
and displacement 26 fixed.

## Ambiguities resolved

- barssince is na before the first cross; a comparison with na is false.
- The opposite closes coincide with the reversing entries. REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
