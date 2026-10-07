# #128250 双均线策略与相对强弱RSI指标组合 -> `fmz_128250_dual_ema_rsi_momentum`

- Source: https://www.fmz.com/strategy/128250 (MyLanguage, author 阿基米德的浴缸, FMZ last modified
  2019-08-20 10:29:50). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Close-price model, completed bars. |
| 2 | ADAPT | 1 % stop/profit threshold -> `sl_atr` x ATR(14) of the entry signal bar. |
| 3 | PASS | OKEX weekly contract in the header only. |
| 4 | DONE | One lot per signal; `SP(BKVOL)`/`BP(SKVOL)` close all. `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`n1` [20, 50, 100] x `n2` [150, 300, 450] x `sl_atr` [1, 2, 3] = **27 trials**. RSI 9, 70/30 fixed.

## Ambiguities resolved

- `SLOSS` default `true` = 1 (MyLanguage booleans are 1/0).
- RSI is the source's own formula (Wilder-style SMA(.,9,1) smoothing of gains over absolute moves).
- Entry is momentum: RSI crossing UP through 70 in an uptrend (not a mean-reversion sell).
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`: EMA order and price above both EMAs; RSI times the entry.

## Marks (2026-10-07)

`none`
