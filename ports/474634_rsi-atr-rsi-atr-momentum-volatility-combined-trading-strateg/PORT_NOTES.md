# #474634 RSI-ATR动量波动组合交易策略-RSI-ATR-Momentum-Volatility-Combined-Trading-Strategy -> `fmz_474634_rsi_sma10_cross_prague_hours_atr_bracket_reversal`

- FMZ source id: 474634 (lineage).
- Source: https://www.fmz.com/strategy/474634 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-11 11:15:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C222). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the tick bracket as ATR multiples from the signal bar's extremes |
| 2 | PASS | RSI / RSI-average crossings in day hours with an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [1.43, 0.5] x `rsi_ma_length` [10, 20]: **4 trials**; the hours and levels fixed.

## Ambiguities resolved

- Ticks as ATR multiples at an interpolated 3-hour reading. ATR threshold as a fraction of 42000. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop`
