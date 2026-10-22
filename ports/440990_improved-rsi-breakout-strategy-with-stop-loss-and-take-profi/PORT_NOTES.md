# #440990 Improved-RSI-Breakout-Strategy-with-Stop-Loss-and-Take-Profit改进RSI突破策略带止损止盈 -> `fmz_440990_rsi_70_30_level_pct_bracket`

- FMZ source id: 440990 (lineage).
- Source: https://www.fmz.com/strategy/440990 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-04 15:27:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C143). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | RSI levels and percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp` [0.02, 0.10] x `sl` [0.10, 0.02]: **4 trials** (the call's values and the constants' names); RSI 14 and levels fixed.

## Ambiguities resolved

- Bracket as passed (target 2 %, stop 10 %). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
