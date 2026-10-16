# #429478 三重EMA追踪止损策略Triple-EMA-With-Trailing-Stop-Loss-Strategy -> `fmz_429478_triple_ema_buffer`

- FMZ source id: 429478 (lineage).
- Source: https://www.fmz.com/strategy/429478 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-17 15:05:41). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | The pip buffer -> an ATR multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() cash quantity and the inert stop inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`buffer_atr` [0.75, 0.25] x `ema3` [50, 100]: **4 trials**; EMA 5 / 20 fixed.

## Ambiguities resolved

- The coded stop is inert. Buffer as an ATR multiple. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
