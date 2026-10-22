# #458185 Fibonacci-Extension-and-Retracement-Channel-Breakout-Strategy-斐波那契延展回撤通道突破策略 -> `fmz_458185_prior_20bar_channel_breakout_state_reversal`

- FMZ source id: 458185 (lineage).
- Source: https://www.fmz.com/strategy/458185 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 16:37:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C203). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Previous-channel breakouts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 55]: **2 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
