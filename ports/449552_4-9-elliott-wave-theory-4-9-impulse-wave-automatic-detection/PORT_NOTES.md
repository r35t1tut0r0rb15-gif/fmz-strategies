# #449552 艾略特波浪理论4-9脉冲波自动检测交易策略-Elliott-Wave-Theory-4-9-Impulse-Wave-Automatic-Detection-Trading-Strategy -> `fmz_449552_three_closes_9bar_momentum_bar_stop_reversal`

- FMZ source id: 449552 (lineage).
- Source: https://www.fmz.com/strategy/449552 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-26 17:32:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C180). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed on the signal bar |
| 2 | PASS | Consecutive closes with a 9-bar momentum filter, signal-bar stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`consclos` [3, 4] x `daysago` [9, 13]: **4 trials**.

## Ambiguities resolved

- Stop at the signal bar's low / high. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`coarse_bar_stop`
