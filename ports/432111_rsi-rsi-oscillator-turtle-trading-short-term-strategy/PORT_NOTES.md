# #432111 海龟交易RSI指标短线策略RSI-Oscillator-Turtle-Trading-Short-term-Strategy -> `fmz_432111_rsi_of_uo_short`

- FMZ source id: 432111 (lineage).
- Source: https://www.fmz.com/strategy/432111 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-14 15:59:25). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C49). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oscillator levels and moving-average order |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 20 % of equity, the risk-based quantity and the partial cover stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [5, 9] x `sell_line` [60, 50]: **4 trials**; UO 5 / 10 / 15, the alligator lengths and the cover line 75 fixed.

## Ambiguities resolved

- Short only. The partial cover and the quantity stop are sizing. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
