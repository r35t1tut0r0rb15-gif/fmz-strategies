# #431400 海龟突破EMA交叉策略Turtle-Breakout-EMA-Cross-Strategy -> `fmz_431400_ema_10_20_tick_bracket`

- FMZ source id: 431400 (lineage).
- Source: https://www.fmz.com/strategy/431400 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-07 15:40:08). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick target / stop -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Lot size 1 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.05, 1.0] x `tp_atr` [0.15, 3.0]: **4 trials**; EMA 10 / 20 and ATR 14 fixed.

## Ambiguities resolved

- Tick bracket as ATR fractions (criterion 2 ADAPT). Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
