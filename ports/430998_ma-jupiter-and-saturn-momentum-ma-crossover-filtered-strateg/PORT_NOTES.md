# #430998 木星与土星动能MA交叉过滤策略Jupiter-and-Saturn-Momentum-MA-Crossover-Filtered-Strategy -> `fmz_430998_ema_diff_map_cross`

- FMZ source id: 430998 (lineage).
- Source: https://www.fmz.com/strategy/430998 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-03 16:13:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Point target / stop -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [12.5, 3.0] x `tp_atr` [5.0, 2.0]: **4 trials**; EMA 20, stdev 2, lookback 504, EMA 50 / SMA 200 and levels 25 / 75 fixed.

## Ambiguities resolved

- Point bracket as ATR fractions of the signal bar (criterion 2 ADAPT). REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_oscillator_pullback"`.

## Marks

`none`
