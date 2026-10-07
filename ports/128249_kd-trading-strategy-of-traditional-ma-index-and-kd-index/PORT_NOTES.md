# #128249 传统均线指标与KD指标的交易策略 -> `fmz_128249_ema_kd_pullback`

- Source: https://www.fmz.com/strategy/128249 (MyLanguage, author 阿基米德的浴缸, FMZ last modified
  2019-08-20 10:30:47). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Close-price model, completed bars. |
| 2 | ADAPT | 2 % stop and 2 % profit threshold -> `sl_atr` x ATR(14) on the latest BK/SK bar. |
| 3 | PASS | BitMEX in the header only. |
| 4 | DONE | Repeated BK/SK (adds, no AUTOFILTER) are sizing; `SP(BKVOL)`/`BP(SKVOL)` close the whole position. `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`n` [60, 120, 240] x `nkd` [5, 9, 14] x `sl_atr` [1, 2, 3] = **27 trials**. KD smoothing 3/3 fixed.

## Ambiguities resolved

- No AUTOFILTER: an add bar moves BKPRICE (the stop and profit references) and is that bar's
  one signal. A BK while short (FMZ: a second, hedged leg) is ignored by the net-position port.
- The entry is a pullback: trend up (C > EMA) with K below D.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_oscillator_pullback"`: trend filter by MA, entry timed by an oscillator
turning against it.

## Marks (2026-10-07)

`none`
