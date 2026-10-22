# #482870 动态-EMA-交叉摆动高低点自适应策略-Dynamic-EMA-Crossover-with-Adaptive-Swing-High-Low-Strategy -> `fmz_482870_ema22_cross_swing14_bracket_reversal`

- FMZ source id: 482870 (lineage).
- Source: https://www.fmz.com/strategy/482870 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:32:58). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C252). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; swing bracket as fractions of the fill |
| 2 | PASS | EMA crossings with swing brackets |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND482870. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [22, 50] x `swing_length` [14, 7]: **4 trials**.

## Ambiguities resolved

- The repeating sell state re-sends the bracket; the opening one is ported, the re-sent case pending.
- MPL 2.0 source, ported and stated. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
