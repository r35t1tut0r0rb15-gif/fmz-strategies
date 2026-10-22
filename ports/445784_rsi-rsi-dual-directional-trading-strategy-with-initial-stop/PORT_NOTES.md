# #445784 RSI双向交易策略与初始止损RSI-Dual-Directional-Trading-Strategy-with-Initial-Stop-Loss -> `fmz_445784_rsi_60_40_cross_rsi_exit_reversal`

- FMZ source id: 445784 (lineage).
- Source: https://www.fmz.com/strategy/445784 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-22 10:44:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C172). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving stop not ported (mark) |
| 2 | PASS | RSI level crossings with RSI exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 100 % of equity size stored; the 6 % stop quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 7] x `upper` [60, 70]: **4 trials**; the lower level 40 fixed.

## Ambiguities resolved

- Moving 6 % stop not ported (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
