# #437550 布林带突破-Swing-交易策略Bollinger-Bands-Breakout-Swing-Trading-Strategy -> `fmz_437550_bollinger_breakout_mid_exit_long`

- FMZ source id: 437550 (lineage).
- Source: https://www.fmz.com/strategy/437550 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-03 16:40:38). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C102). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `mult` [2.0, 1.5]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
