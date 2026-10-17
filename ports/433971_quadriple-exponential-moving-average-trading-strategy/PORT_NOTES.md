# #433971 Quadriple Exponential Moving Average Trading Strategy -> `fmz_433971_quad_ema_cross_bracket`

- FMZ source id: 433971 (lineage).
- Source: https://www.fmz.com/strategy/433971 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-01 18:29:07). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C64). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick distances -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 10000 cash quantity and the tick bracket stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.015, 0.5] x `slow` [55, 89]: **4 trials**; EMA 8 / 13 / 21, target = sl x 1000 / 150 and ATR 14 fixed.

## Ambiguities resolved

- Bracket only on the stacked entry from flat, tracked on bar highs / lows; tick distances as ATR. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
