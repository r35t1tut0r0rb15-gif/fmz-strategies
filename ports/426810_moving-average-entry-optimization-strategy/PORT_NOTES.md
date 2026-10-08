# #426810 Moving Average Entry Optimization Strategy -> `fmz_426810_delayed_ma_entry`

- Source: https://www.fmz.com/strategy/426810 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-14 16:52:30). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Price threshold -> ATR(14) multiple on the bar. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [20, 50] x `maxwait` [3, 6] x `thr_atr` [0, 0.25, 0.5]: **12 trials**, defaults 20 / 3 / 0 (the source's; 0.01 price units is 0 ATR on BTC).

## Ambiguities resolved

- Flat = position at the bar close; a close and an entry never share a bar.
- As written a flip while long sets signal -1, while short +1.
- Criterion 2 (ADAPT): threshold -> thr_atr x ATR(14) on the bar.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
