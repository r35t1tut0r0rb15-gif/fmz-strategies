# #428794 动态止损随ATR波动自适应的动量敲入策略Dynamic-Stop-Loss-Strategy-Adaptive-to-ATR-Fluctuations -> `fmz_428794_stoch_vs_rsi_of_atr`

- FMZ source id: 428794 (lineage).
- Source: https://www.fmz.com/strategy/428794 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-09 15:30:29). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels only (the ATR enters through its RSI). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [34, 14] x `offset` [10, 0]: **4 trials**; K smoothing 2 fixed.

## Ambiguities resolved

- Skip bars place no entry (cancel_all). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
