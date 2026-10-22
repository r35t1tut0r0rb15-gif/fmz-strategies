# #458023 基于RSI的低价动态入场与止损策略-Dynamic-Low-Price-Entry-and-Stop-Loss-Strategy-Based-on-RSI -> `fmz_458023_rsi_of_lows_dip_loss_test_long`

- FMZ source id: 458023 (lineage).
- Source: https://www.fmz.com/strategy/458023 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-29 13:22:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C198). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the loss exit is a close test |
| 2 | PASS | RSI-of-lows dips |
| 3 | PASS | No exchange named. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `entry_lvl` [24, 30] x `exit_lvl` [72, 60]: **8 trials**; the 20 % loss fixed.

## Ambiguities resolved

- No bar size (bar_size_pending). Long only.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`bar_size_pending`
